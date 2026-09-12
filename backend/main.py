import os
import io
from typing import Optional, List
from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from datetime import datetime
from dotenv import load_dotenv
import pypdf
import docx

from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict

# Load environment variables (.env file containing GROQ_API_KEY)
load_dotenv()

# ==========================================
# 1. DATABASE CONFIGURATION (SQLAlchemy)
# ==========================================
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./qms_complaints.db")

engine = create_engine(
    DATABASE_URL, 
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class ComplaintModel(Base):
    __tablename__ = "complaints"

    id = Column(Integer, primary_key=True, index=True)
    complaint_source = Column(String(255), nullable=True)
    customer_name = Column(String(255), nullable=True)
    product_name = Column(String(255), nullable=True)
    batch_number = Column(String(255), nullable=True)
    manufacturing_date = Column(String(100), nullable=True)
    expiry_date = Column(String(100), nullable=True)
    quantity_affected = Column(String(100), nullable=True)
    complaint_type = Column(String(255), nullable=True)
    complaint_date = Column(String(100), nullable=True)
    detailed_description = Column(Text, nullable=True)
    initial_severity = Column(String(100), nullable=True)
    priority = Column(String(100), nullable=True)
    ai_risk_verdict = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# 2. PYDANTIC SCHEMAS FOR API & AGENT
# ==========================================
class ComplaintDetailsSchema(BaseModel):
    complaint_source: Optional[str] = Field(None, description="Source of complaint (Email, Phone, etc.)")
    customer_name: Optional[str] = Field(None, description="Reporting customer or facility name")
    product_name: Optional[str] = Field(None, description="Name of the pharmaceutical product")
    batch_number: Optional[str] = Field(None, description="Batch/Lot Number")
    manufacturing_date: Optional[str] = Field(None, description="Manufacturing Date")
    expiry_date: Optional[str] = Field(None, description="Expiry Date")
    quantity_affected: Optional[str] = Field(None, description="Quantity affected")
    complaint_type: Optional[str] = Field(None, description="Type/Category of complaint")
    complaint_date: Optional[str] = Field(None, description="Date complaint occurred or reported")
    detailed_description: Optional[str] = Field(None, description="Comprehensive description of the defect or event")

class TriageAssessmentSchema(BaseModel):
    initial_severity: Optional[str] = Field(None, description="Initial Severity level (Critical, High, Medium, Low)")
    priority: Optional[str] = Field(None, description="Priority level (High, Medium, Low)")
    ai_risk_verdict: Optional[str] = Field(None, description="2-3 sentence AI assessment explaining risk rationale")

class ExtractedComplaintSchema(BaseModel):
    details: ComplaintDetailsSchema
    triage: TriageAssessmentSchema

class ExtractTextRequest(BaseModel):
    text: str

class ChatRefinementRequest(BaseModel):
    prompt: str
    current_form_data: ExtractedComplaintSchema

# ==========================================
# 3. LANGGRAPH AI AGENT WORKFLOW
# ==========================================
class AgentState(TypedDict):
    raw_text: str
    extracted_data: dict

def extract_complaint_node(state: AgentState):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is missing.")

    llm = ChatGroq(temperature=0, model="openai/gpt-oss-20b", groq_api_key=api_key)
    structured_llm = llm.with_structured_output(ExtractedComplaintSchema)
    
    prompt = f"""
    You are an expert Pharmaceutical Quality Assurance (QA) assistant.
    Analyze the following customer complaint document/text and extract all relevant structured parameters.
    Evaluate the pharmaceutical safety risk to assign initial severity and priority, providing a clear explanation in ai_risk_verdict.

    Document Content:
    {state['raw_text']}
    """
    
    result = structured_llm.invoke(prompt)
    return {"extracted_data": result.model_dump()}

workflow = StateGraph(AgentState)
workflow.add_node("extract_complaint", extract_complaint_node)
workflow.set_entry_point("extract_complaint")
workflow.add_edge("extract_complaint", END)
complaint_agent = workflow.compile()

# ==========================================
# 4. FASTAPI APP & ENDPOINTS
# ==========================================
app = FastAPI(title="Aivoa Pharma QMS Complaint Engine", version="1.0.0")
@app.get("/")
async def root():
    return {"message": "Aivoa API is running. Visit /docs to test the endpoints."}
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def extract_text_from_file(file: UploadFile) -> str:
    content = file.file.read()
    filename = file.filename.lower()
    
    if filename.endswith(".pdf"):
        reader = pypdf.PdfReader(io.BytesIO(content))
        return "\n".join([page.extract_text() or "" for page in reader.pages])
    elif filename.endswith(".docx"):
        doc = docx.Document(io.BytesIO(content))
        return "\n".join([p.text for p in doc.paragraphs])
    elif filename.endswith((".txt", ".eml")):
        return content.decode("utf-8", errors="ignore")
    else:
        raise HTTPException(status_code=400, detail="Unsupported file format.")

@app.post("/api/extract", response_model=ExtractedComplaintSchema)
async def extract_complaint_data(
    text: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None)
):
    raw_content = ""
    if file:
        raw_content = extract_text_from_file(file)
    elif text:
        raw_content = text
    else:
        raise HTTPException(status_code=400, detail="Please provide either text or a file.")

    if not raw_content.strip():
        raise HTTPException(status_code=400, detail="Extracted content is empty.")

    output = complaint_agent.invoke({"raw_text": raw_content})
    return output["extracted_data"]

@app.post("/api/chat/refine", response_model=ExtractedComplaintSchema)
async def refine_complaint_with_chat(request: ChatRefinementRequest):
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise HTTPException(status_code=500, detail="GROQ_API_KEY environment variable is missing.")

    llm = ChatGroq(temperature=0, model="openai/gpt-oss-20b", groq_api_key=api_key)
    structured_llm = llm.with_structured_output(ExtractedComplaintSchema)
    
    prompt = f"""
    You are an AI assistant helping a Quality Assurance engineer update a complaint form.
    Current Form State:
    {request.current_form_data.model_dump_json(indent=2)}

    User Instruction / Update Request:
    "{request.prompt}"

    Apply the requested changes to the relevant fields while preserving existing correct details. Update ai_risk_verdict if risk parameters change.
    """
    
    result = structured_llm.invoke(prompt)
    return result

@app.post("/api/complaints")
async def save_complaint(data: ExtractedComplaintSchema, db: Session = Depends(get_db)):
    db_record = ComplaintModel(
        complaint_source=data.details.complaint_source,
        customer_name=data.details.customer_name,
        product_name=data.details.product_name,
        batch_number=data.details.batch_number,
        manufacturing_date=data.details.manufacturing_date,
        expiry_date=data.details.expiry_date,
        quantity_affected=data.details.quantity_affected,
        complaint_type=data.details.complaint_type,
        complaint_date=data.details.complaint_date,
        detailed_description=data.details.detailed_description,
        initial_severity=data.triage.initial_severity,
        priority=data.triage.priority,
        ai_risk_verdict=data.triage.ai_risk_verdict
    )
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    return {"status": "success", "complaint_id": db_record.id, "message": "Complaint logged successfully."}

@app.get("/api/complaints")
async def list_complaints(db: Session = Depends(get_db)):
    return db.query(ComplaintModel).all()