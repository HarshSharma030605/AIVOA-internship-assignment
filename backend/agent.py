from typing import TypedDict
from backend.models import ExtractedComplaint
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
import os

# 1. Define the State
class AgentState(TypedDict):
    raw_text: str
    extracted_data: dict
    chat_history: list

# 2. Define the Extraction Node
def extract_complaint_node(state: AgentState):
    llm = ChatGroq(temperature=0, model="gemma2-9b-it") # Or llama-3.3-70b-versatile for better reasoning
    structured_llm = llm.with_structured_output(ExtractedComplaint)
    
    prompt = f"""
    You are a pharmaceutical Quality Assurance AI. 
    Extract the QMS data from the following complaint text.
    
    Critically evaluate the text to determine 'initial_severity' and 'priority'.
    Provide a clear, professional 'ai_risk_verdict' explaining your risk classification.
    
    Text:
    {state['raw_text']}
    """
    
    result = structured_llm.invoke(prompt)
    return {"extracted_data": result.dict()}

# 3. Build the Graph
workflow = StateGraph(AgentState)
workflow.add_node("extract", extract_complaint_node)
workflow.set_entry_point("extract")
workflow.add_edge("extract", END)

complaint_agent = workflow.compile()

