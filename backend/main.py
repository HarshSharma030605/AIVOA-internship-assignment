import os
import io
import json
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
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END
from typing_extensions import TypedDict

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
# 2. FLATTENED PYDANTIC SCHEMAS
# ==========================================
class ExtractedComplaintSchema(BaseModel):
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
    
    initial_severity: Optional[str] = Field(None, description="Initial Severity level (Critical, High, Medium, Low)")
    priority: Optional[str] = Field(None, description="Priority level (High, Medium, Low)")
    ai_risk_verdict: Optional[str] = Field(None, description="2-3 sentence AI assessment explaining risk rationale")
    root_cause_recommendations: List[str] = Field(default_factory=list, description="Top 2-3 probable technical or manufacturing root causes")
    immediate_containment: Optional[str] = Field(default=None, description="Immediate action required (e.g., quarantine lot)")
    corrective_action: Optional[str] = Field(default=None, description="Action to remediate existing issue")
    preventive_action: Optional[str] = Field(default=None, description="Action to prevent future recurrence")
    fda_reportable: bool = Field(default=False, description="True if event involves severe adverse reaction, patient harm, hospitalization, or death requiring FDA reporting")
    fda_reasoning: Optional[str] = Field(default=None, description="Regulatory justification for FDA reportability status")

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
    Evaluate the pharmaceutical safety risk, assign initial severity, priority, and provide:
    1. Top 2-3 probable technical or manufacturing Root Causes.
    2. Actionable CAPA recommendations (Immediate Containment, Corrective Action, Preventive Action).
    3. FDA Adverse Event Flagging (set fda_reportable=True if patient harm, severe reaction, hospitalization, or life-threatening symptoms occurred, with brief justification in fda_reasoning).

    Document Content:
    {state['raw_text']}
    """
    
    result = structured_llm.invoke(prompt)
    print("DEBUG - LLM Extracted Result:", result)
    return {"extracted_data": result.model_dump()}

workflow = StateGraph(AgentState)
workflow.add_node("extract_complaint", extract_complaint_node)
workflow.set_entry_point("extract_complaint")
workflow.add_edge("extract_complaint", END)
complaint_agent = workflow.compile()

# ==========================================
# 4. FASTAPI APP & ENDPOINTS
# ==========================================
app = FastAPI(title="Aivoa Pharma QMS Complaint Engine", version="1.1.0")

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
    
    system_prompt = """You are an expert Pharmaceutical Quality Assurance (QA) assistant helping a engineer update a complaint form.
You must update the form fields according to the user instruction while preserving all other valid data.
You MUST output a valid JSON object matching the exact keys of the ExtractedComplaintSchema:
- complaint_source (string or null)
- customer_name (string or null)
- product_name (string or null)
- batch_number (string or null)
- manufacturing_date (string or null)
- expiry_date (string or null)
- quantity_affected (string or null)
- complaint_type (string or null)
- complaint_date (string or null)
- detailed_description (string or null)
- initial_severity (string or null)
- priority (string or null)
- ai_risk_verdict (string or null)
- root_cause_recommendations (array of strings)
- immediate_containment (string or null)
- corrective_action (string or null)
- preventive_action (string or null)
- fda_reportable (boolean)
- fda_reasoning (string or null)

Return ONLY raw JSON or JSON inside markdown code blocks. Do not add conversational text."""

    user_prompt = f"""
Current Form State:
{request.current_form_data.model_dump_json(indent=2)}

User Instruction / Update Request:
"{request.prompt}"
"""

    messages = [
        SystemMessage(content=system_prompt),
        HumanMessage(content=user_prompt)
    ]
    
    response = llm.invoke(messages)
    raw_text = response.content.strip()

    # Clean markdown code blocks if present
    if raw_text.startswith("```json"):
        raw_text = raw_text[7:]
    elif raw_text.startswith("```"):
        raw_text = raw_text[3:]
    if raw_text.endswith("```"):
        raw_text = raw_text[:-3]
        
    cleaned_text = raw_text.strip()

    try:
        updated_data = json.loads(cleaned_text)
        return updated_data
    except json.JSONDecodeError as e:
        print(f"JSON Parse Error: {e}\nRaw Content was: {response.content}")
        raise HTTPException(status_code=500, detail="Failed to parse LLM refinement response as JSON.")

@app.post("/api/complaints")
def save_complaint(data: ExtractedComplaintSchema, db: Session = Depends(get_db)):
    try:
        # Map flat Pydantic model directly to database columns
        db_data = {
            "complaint_source": data.complaint_source,
            "customer_name": data.customer_name,
            "product_name": data.product_name,
            "batch_number": data.batch_number,
            "manufacturing_date": data.manufacturing_date,
            "expiry_date": data.expiry_date,
            "quantity_affected": data.quantity_affected,
            "complaint_type": data.complaint_type,
            "complaint_date": data.complaint_date,
            "detailed_description": data.detailed_description,
            "initial_severity": data.initial_severity,
            "priority": data.priority,
            "ai_risk_verdict": data.ai_risk_verdict,
            "created_at": datetime.utcnow()
        }
        
        db_complaint = ComplaintModel(**db_data)
        db.add(db_complaint)
        db.commit()
        db.refresh(db_complaint)
        
        return {"message": "Complaint saved successfully!", "id": db_complaint.id}
        
    except Exception as e:
        db.rollback()
        print(f"Database save error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/complaints")
async def list_complaints(db: Session = Depends(get_db)):
    records = db.query(ComplaintModel).all()
    results = []
    for r in records:
        d = r.__dict__.copy()
        d.pop("_sa_instance_state", None)
        results.append(d)
    return results