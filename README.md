


# Aivoa Pharma QMS // Intelligent Complaint Ingestion & Management Engine

A modern, full-stack Quality Management System (QMS) designed to automate the intake, extraction, safety risk evaluation, and database persistence of pharmaceutical customer complaints and adverse event reports.

---

## 🤖 AI Usage Clause

> **Development & Authorship Disclosure:** 
> The core logic, architectural design, domain-specific workflows, and system requirements for this project were entirely conceived and directed by the author (**Harsh Sharma**). The code implementation, syntax generation, boilerplate structuring, and debugging assistance were completed with the aid of AI collaborators.

---

## 🌟 Key Features

* **Multi-Format Ingestion:** Seamlessly upload unstructured PDF, Word (`.docx`), TXT, or EML files, or paste raw text reports directly.
* **AI-Powered Extraction:** Leverages LangGraph and Groq LLMs to automatically extract key medical and logistical attributes (Batch numbers, product names, expiry dates, quantities).
* **Automated Risk & CAPA Assessment:** Automatically determines initial severity, priority, risk verdicts, and generates structured Corrective and Preventive Action (CAPA) plans.
* **Regulatory Flagging:** Automatically detects potential adverse events and flags cases requiring mandatory FDA reporting with regulatory justifications.
* **Interactive Chat Refinement:** Allows quality assurance officers to adjust form parameters conversationally using a built-in AI assistant interface.
* **Reliable Persistence:** Backed by FastAPI and SQLAlchemy for secure, structured relational storage and audit trail management.

---

## 🛠️ Tech Stack

* **Backend:** FastAPI, Python, SQLAlchemy, Pydantic v2
* **AI & Orchestration:** LangChain, LangGraph, Groq API (`openai/gpt-oss-20b`)
* **Document Processing:** `pypdf`, `python-docx`
* **Database:** SQLite (`qms_complaints.db`)
* **Frontend State & UI:** React, Redux Toolkit, Modern Split-Screen Workspace

---

## 📂 Project Architecture

```text
AIVOA-internship-assignment/
├── backend/
│   ├── main.py              # FastAPI application, database models, and LangGraph workflow
│   └── qms_complaints.db    # SQLite relational database (auto-generated)
├── frontend/                # React & Redux UI workspace
├── requirements.txt         # Python dependencies
└── README.md                # Project documentation

```

---

## 🚀 Getting Started & Installation

### 1. Clone the Repository & Navigate to the Project

```bash
git clone [https://github.com/your-username/aivoa-pharma-qms.git](https://github.com/your-username/aivoa-pharma-qms.git)
cd aivoa-pharma-qms

```

### 2. Set Up a Python Virtual Environment

```bash
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

```

### 3. Install Dependencies

```bash
pip install fastapi uvicorn sqlalchemy pydantic python-dotenv pypdf python-docx langchain-groq langgraph langchain-core

```

### 4. Configure Environment Variables

Create a `.env` file in your root directory and add your Groq API key:

```env
GROQ_API_KEY=your_actual_groq_api_key_here
DATABASE_URL=sqlite:///./qms_complaints.db

```

### 5. Run the Backend Server

Start the FastAPI server using Uvicorn:

```bash
uvicorn backend.main:app --reload --port 8000

```

The API documentation and interactive Swagger UI will be available at: `http://localhost:8000/docs`

---

## 🔌 Core API Endpoints

* `POST /api/extract` — Accepts raw text or uploaded documents (`.pdf`, `.docx`, `.txt`) and returns structured compliance JSON.
* `POST /api/chat/refine` — Processes natural language chat instructions from quality officers to update and refine current form state.
* `POST /api/complaints` — Saves validated complaint records into the relational database.
* `GET /api/complaints` — Retrieves all stored complaint and audit records.

