# Strategillent

## AI Transformation Strategy Intelligence

Strategillent is an AI-powered transformation intelligence application that connects organisational context with structured external research to identify strategic issues, transformation opportunities, priorities, and recommended initiatives.

The application demonstrates the following transformation intelligence flow:

**Organisation Context → External Evidence → Strategic Issues → Transformation Opportunities → Priorities → Initiatives → Outcomes**

---

# Demonstration Case

## FinNova

FinNova is a fictional digital payments and consumer lending organisation created as the demonstration case for this project.

The project includes structured external research covering:

- AI
- Fraud
- Lending
- Customer Experience
- Governance
- Data

The external research dataset contains evidence from regulators, central banks, international financial institutions, and research organisations.

Fictional organisation information and external research are kept separate so that organisational assumptions are not presented as external facts.

---

# Application Architecture

Strategillent follows a layered application architecture:

```text
┌──────────────────────────────────────────────┐
│                 USER INTERFACE               │
│              React + TypeScript              │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│              APPLICATION / API               │
│                   FastAPI                    │
│                                              │
│ Organisation APIs                            │
│ Research APIs                                │
│ Intelligence APIs                            │
│ Question APIs                                │
└──────────────────────┬───────────────────────┘
                       │
              ┌────────┴────────┐
              ▼                 ▼
┌──────────────────────┐ ┌─────────────────────┐
│   AI INTELLIGENCE    │ │      RETRIEVAL      │
│                      │ │                     │
│ Ollama / Llama 3.2   │ │ Evidence Search &   │
│ Strategic Analysis   │ │ Relevance Ranking   │
│ Answer Generation    │ │                     │
└──────────┬───────────┘ └──────────┬──────────┘
           │                        │
           └────────────┬───────────┘
                        ▼
┌──────────────────────────────────────────────┐
│               DATA & KNOWLEDGE               │
│                                              │
│             SQLite + SQLAlchemy              │
│                                              │
│ Organisations                                │
│ Objectives                                   │
│ Evidence                                     │
│ Research Sources                             │
│ Strategic Issues                             │
│ Transformation Dimensions                    │
│ Opportunities                                │
│ Initiatives                                 │
│ Analysis Runs                                │
│ Relationships                                │
└──────────────────────┬───────────────────────┘
                       ▲
                       │
┌──────────────────────────────────────────────┐
│          EXTERNAL RESEARCH / DATA            │
│                                              │
│        Structured Research Dataset           │
│        Regulators / Institutions             │
└──────────────────────────────────────────────┘
````

The architecture separates the user interface, application/API layer, AI intelligence, retrieval, persistent data, and external research.

---

# Technology Stack

## Frontend

* React
* TypeScript
* Vite
* React Router
* Lucide React

## Backend

* Python
* FastAPI
* SQLAlchemy
* SQLite
* Pydantic

## AI

* Ollama
* Llama 3.2

The AI model runs locally through Ollama.

## Testing

* Pytest

The application uses locally reproducible and freely available technologies without requiring a paid software licence.

---

# Project Structure

```text
Strategillent/
│
├── backend/
│   ├── app/
│   │   ├── ai/
│   │   ├── api/
│   │   ├── core/
│   │   ├── models/
│   │   ├── retrieval/
│   │   ├── schemas/
│   │   ├── seed/
│   │   ├── services/
│   │   ├── utils/
│   │   └── main.py
│   │
│   ├── scripts/
│   │   └── seed.py
│   │
│   ├── tests/
│   └── requirements.txt
│
├── data/
│   └── seed/
│       ├── evidence.json
│       ├── organisation.json
│       └── transformation_dimensions.json
│
├── research/
│   ├── external_evidence.json
│   ├── finnova_context.json
│   ├── research_notes.md
│   └── transformation_dimensions.json
│
├── frontend/
│   ├── src/
│   ├── package.json
│   ├── package-lock.json
│   └── vite.config.ts
│
├── README.md
├── .env.example
└── .gitignore
```

---

# Setup

## Prerequisites

Install:

* Python 3.12+
* Node.js
* npm
* Ollama

---

## 1. Start Ollama

Make sure Ollama is installed and the Llama 3.2 model is available.

```bash
ollama run llama3.2
```

Keep Ollama running while using the application.

---

## 2. Start the Backend

Open a terminal from the project root:

```bash
cd backend
```

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Start the FastAPI server:

```bash
uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

---

## 3. Start the Frontend

Open another terminal from the project root:

```bash
cd frontend
```

Install dependencies:

```bash
npm install
```

Start the frontend:

```bash
npm run dev
```

Open the URL displayed by Vite, normally:

```text
http://localhost:5173
```

---

# Data and Research

The project contains structured seed and research data.

## Seed Data

Located in:

```text
data/seed/
```

This contains:

* Demonstration organisation
* Evidence
* Transformation dimensions

## Research Data

Located in:

```text
research/
```

This contains:

* External evidence
* FinNova organisational context
* Transformation dimensions
* Research notes

The demonstration research dataset contains **32 evidence records**.

Each evidence record separates:

* Claim
* Supporting evidence
* Strategic implication
* Source information

This structure allows the application to distinguish external evidence from strategic interpretation.

---

# Application Flow

## 1. Organisation Context

The application stores organisational information including:

* Organisation name
* Industry
* Business model
* Markets
* Customers
* Employees
* Products
* Challenges

Organisation records are persisted in the database and can be accessed through the backend APIs.

---

## 2. Intelligence Analysis

The intelligence pipeline combines organisational context with relevant evidence.

It identifies:

* Strategic issues
* Supporting evidence
* Transformation opportunities
* Priorities
* Recommended initiatives

The backend processes structured records rather than relying on manually prepared presentation content.

---

## 3. Evidence Retrieval

The retrieval layer searches the structured evidence collection and ranks relevant records based on their relevance to the analysis or question.

Relevant evidence is then supplied to the AI layer as contextual input.

---

## 4. AI Intelligence

Ollama runs Llama 3.2 locally.

AI is used for tasks including:

* Strategic issue analysis
* Evidence interpretation
* Transformation opportunity generation
* Intelligence answer generation

The prompts instruct the model to use the supplied organisation context and evidence and not invent facts, statistics, or sources.

---

## 5. Evidence Traceability

Evidence is stored with source information and strategic implications.

Strategic issues and opportunities can be associated with supporting evidence records.

Intelligence answers also return the evidence IDs used for the generated response.

This provides a traceable connection between:

```text
Research Evidence
       ↓
Strategic Analysis
       ↓
Transformation Opportunity
       ↓
Recommended Initiative
```

---

## 6. Prioritisation

Transformation opportunities are prioritised using deterministic application logic.

The priority score is calculated using:

```text
Priority =
    0.35 × Business Impact
  + 0.20 × Feasibility
  + 0.20 × Urgency
  + 0.15 × Strategic Alignment
  + 0.10 × Evidence Confidence
```

This keeps prioritisation predictable and separates the scoring mechanism from LLM-generated text.

---

## 7. Intelligence Q&A

The application provides an intelligence Q&A capability for interrogating the resulting analysis.

Example:

> What should this organisation transform, why, what evidence supports it, and what should be done first?

The answer is generated using the organisation context and retrieved evidence rather than a hard-coded response.

The response also returns the evidence IDs used to generate the answer.

---

# Persistence and Data Model

Strategillent uses SQLite with SQLAlchemy for persistent application data.

The data model includes:

* Organisations
* Objectives
* Evidence
* Research Sources
* Strategic Issues
* Transformation Dimensions
* Opportunities
* Initiatives
* Analysis Runs
* Relationships

The application separates organisational context from external evidence:

```text
Organisation Context
        +
External Evidence
        ↓
Strategic Analysis
        ↓
Transformation Intelligence
```

This ensures that fictional organisation assumptions are not treated as external research facts.

Analysis runs retain model and analysis-version information to support traceability.

---

# Dynamic Processing

The application is designed around persisted records and reusable backend services rather than static presentation output.

The workflow supports:

```text
Input
  ↓
API
  ↓
Database / Knowledge
  ↓
Retrieval
  ↓
AI Analysis
  ↓
Persistence
  ↓
Relationships
  ↓
Output
```

The same application workflow can process new organisation records and new intelligence questions without requiring a new static page or manually prepared response.

The current demonstration is configured around the FinNova scenario and its structured transformation domains.

---

# Testing

Automated backend tests are located in:

```text
backend/tests/
```

Run the test suite from the backend directory:

```bash
pytest
```

The test suite covers:

* Organisation APIs
* Research APIs
* Intelligence processing
* Prioritisation
* Intelligence questions

The current test suite passes successfully.

---

# AI and Model Information

Strategillent uses:

```text
Ollama
Llama 3.2
```

The model is executed locally through Ollama.

This avoids dependence on a paid hosted LLM API for the demonstration.

If Ollama or the selected local model is unavailable, AI-dependent analysis and Q&A cannot generate new model output until a compatible local or migrated model endpoint is configured.

The LLM integration is isolated in the AI layer, allowing the model endpoint to be replaced without changing the overall application architecture.

---

# Library and Licence Inventory

| Technology   | Purpose                | Licence / Availability |
| ------------ | ---------------------- | ---------------------- |
| React        | Frontend UI            | MIT                    |
| TypeScript   | Frontend development   | Apache-2.0             |
| Vite         | Frontend build tooling | MIT                    |
| React Router | Frontend routing       | MIT                    |
| Lucide React | UI icons               | ISC                    |
| Python       | Backend runtime        | PSF License            |
| FastAPI      | Backend API framework  | MIT                    |
| SQLAlchemy   | Database ORM           | MIT                    |
| SQLite       | Persistent database    | Public domain          |
| Pydantic     | Data validation        | MIT                    |
| Pytest       | Automated testing      | MIT                    |
| Ollama       | Local LLM runtime      | MIT                    |
| Llama 3.2    | Local language model   | Meta Llama licence     |

Licence terms should be checked against the exact versions distributed with the final environment before production or commercial use.

---

# AI-Assisted Development Disclosure

AI coding assistants were used during development to assist with:

* Code generation
* Implementation
* Debugging
* Refactoring
* Documentation

The resulting application was assembled, tested, and validated as part of the challenge submission.

The AI application itself is separately powered by a locally running Ollama/Llama 3.2 model.

---

# Demonstration Flow

The recommended demonstration sequence is:

1. Open Strategillent
2. Select FinNova
3. Show the organisation context
4. Run Intelligence
5. Review strategic issues
6. Inspect supporting evidence
7. Review transformation opportunities
8. Review deterministic prioritisation
9. Ask an intelligence question
10. Show the evidence-backed answer
11. Demonstrate how organisational context, evidence, analysis, and recommendations are connected

---

# Design Principles

Strategillent was designed around:

* Structured intelligence rather than hard-coded answers
* Separation of organisational context and external evidence
* Persistent storage
* Evidence traceability
* Modular backend services
* Reusable AI components
* Deterministic prioritisation
* Local AI execution
* Automated testing
* Data-driven transformation analysis
* Separation of AI reasoning from application logic

---

# Scope and Limitations

FinNova is the primary demonstration scenario for this submission.

The application architecture uses reusable concepts such as:

* Organisations
* Evidence
* Research Sources
* Strategic Issues
* Transformation Dimensions
* Opportunities
* Initiatives
* Analysis Runs

The current implementation focuses on the supplied FinNova research dataset and its six transformation domains.

The architecture is designed so that additional organisations, evidence domains, transformation dimensions, retrieval strategies, and analysis logic can be added without redesigning the entire application.

For larger production workloads, the persistence layer could be migrated from SQLite to PostgreSQL and retrieval/analysis could be moved to asynchronous background processing.

---


