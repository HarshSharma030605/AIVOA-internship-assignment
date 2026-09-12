from pydantic import BaseModel, Field
from typing import Optional

class ComplaintDetails(BaseModel):
    complaint_source: Optional[str] = Field(description="Source of the complaint, e.g., Email, Phone, Distributor")
    customer_name: Optional[str] = Field(description="Name of the reporting customer or facility")
    product_name: Optional[str] = Field(description="Name of the pharmaceutical product")
    batch_number: Optional[str] = Field(description="Alphanumeric batch or lot number")
    manufacturing_date: Optional[str] = Field(description="Date of manufacturing")
    expiry_date: Optional[str] = Field(description="Date of product expiry")
    quantity_affected: Optional[str] = Field(description="Quantity of product affected")
    complaint_type: Optional[str] = Field(description="Category of the issue, e.g., Quality, Packaging, Efficacy")
    complaint_date: Optional[str] = Field(description="Date the complaint was initially reported")
    detailed_description: Optional[str] = Field(description="Comprehensive summary of the issue")

class TriageAssessment(BaseModel):
    initial_severity: Optional[str] = Field(description="Risk level: Critical, High, Medium, or Low")
    priority: Optional[str] = Field(description="Action priority: High, Medium, or Low")
    # NEW: NLP Verdict for the AI Copilot Risk Assessment panel
    ai_risk_verdict: Optional[str] = Field(description="A 2-3 sentence natural language explanation justifying the chosen severity and priority based on pharmaceutical risk.")

class ExtractedComplaint(BaseModel):
    details: ComplaintDetails
    triage: TriageAssessment