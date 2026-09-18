
````
# Strategillent

## AI Transformation Strategy Intelligence

Strategillent is an AI-powered transformation intelligence application that connects organisational context with structured external research to identify strategic issues, transformation opportunities, priorities, and recommended initiatives.

The application demonstrates the following transformation intelligence flow:

**Organisation Context → External Evidence → Strategic Issues → Transformation Opportunities → Priorities → Initiatives → Outcomes**

---

## Demonstration Case

### FinNova

FinNova is a fictional digital payments and consumer lending organisation created as the demonstration case for this project.

The project includes structured external research covering topics such as:

- AI
- Fraud
- Lending
- Customer Experience
- Governance
- Data

The external research dataset contains evidence from regulators, central banks, international financial institutions, and research organisations.

Fictional organisation information and external research are kept separate so that organisational assumptions are not presented as external facts.

---

## Architecture

```text
┌──────────────────────────────────────────────┐
│                USER INTERFACE                │
│              React + TypeScript              │
└──────────────────────┬───────────────────────┘
                       │
                       ▼
┌──────────────────────────────────────────────┐
│              APPLICATION / API               │
│                   FastAPI                    │
└──────────────────────┬───────────────────────┘
                       │
             ┌─────────┴─────────┐
             ▼                   ▼
┌──────────────────────┐ ┌─────────────────────┐
│   AI INTELLIGENCE    │ │      RETRIEVAL      │
│                      │ │                     │
│ Ollama / Llama 3.2   │ │ Evidence Search &   │
│ Strategic Analysis   │ │ Relevance Ranking   │
└──────────┬───────────┘ └──────────┬──────────┘
           │                        │
           └────────────┬───────────┘
                        ▼
┌──────────────────────────────────────────────┐
│             DATA & KNOWLEDGE                │
│                                              │
│          SQLite + SQLAlchemy                 │
│                                              │
│ Organisations                                │
│ Evidence                                     │
│ Research Sources                             │
│ Strategic Issues                             │
│ Transformation Dimensions                    │
│ Opportunities                                │
│ Initiatives                                  │
│ Analysis Runs                                │
│ Relationships                                │
└──────────────────────┬───────────────────────┘
                       ▲
                       │
┌──────────────────────────────────────────────┐
│          EXTERNAL RESEARCH / DATA            │
│                                              │
│       Structured Research Dataset            │
│       Regulators / Institutions              │
└──────────────────────────────────────────────┘
````

---

## Technology Stack

### Frontend

* React
* TypeScript
* Vite
* React Router

### Backend

* Python
* FastAPI
* SQLAlchemy
* SQLite
* Pydantic

### AI

* Ollama
* Llama 3.2

The AI model runs locally through Ollama.

### Testing

* Pytest

---

## Project Structure

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

### Seed Data

Located in:

```
data/seed/
```

This contains the demonstration organisation, evidence, and transformation dimensions.

### Research Data

Located in:

```text
research/
```

This contains:

* External evidence
* FinNova organisational context
* Transformation dimensions
* Research notes

The demonstration research dataset contains 32 evidence records.

Each evidence record separates:

* Claim
* Supporting evidence
* Strategic implication
* Source information

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

---

## 2. Intelligence Analysis

The intelligence pipeline combines organisational context with relevant evidence.

It identifies:

* Strategic issues
* Supporting evidence
* Transformation opportunities
* Priorities
* Recommended initiatives

---

## 3. Evidence

Evidence is stored with source information and strategic implications.

This allows recommendations to be traced back to their underlying research.

---

## 4. Prioritisation

Transformation opportunities are prioritised using deterministic application logic.

This keeps prioritisation predictable rather than relying entirely on an LLM-generated ranking.

---

## 5. Intelligence Q&A

The application provides an intelligence Q&A capability for interrogating the resulting analysis.

Example:

> What should this organisation transform, why, what evidence supports it, and what should be done first?

The answer is generated using the organisation context, retrieved evidence, and stored intelligence rather than a hard-coded response.

---

# Persistence and Traceability

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

# AI Usage

Strategillent uses:

```text
Ollama
Llama 3.2
```

The model is executed locally through Ollama.

AI is used for:

* Strategic issue analysis
* Evidence interpretation
* Transformation opportunity generation
* Intelligence answer generation

Deterministic application logic is used where predictable behaviour is preferred, including prioritisation and data processing.

---

# AI-Assisted Development Disclosure

AI coding assistants were used during development to assist with:

* Code generation
* Implementation
* Debugging
* Refactoring
* Documentation

The resulting application was assembled, tested, and validated as part of the challenge submission.

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
8. Review prioritisation
9. Ask an intelligence question
10. Demonstrate how the resulting intelligence connects organisational context, evidence, analysis, and recommendations

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

---

# Scope

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

The current demonstration focuses on the supplied FinNova research dataset and demonstrates the complete transformation intelligence workflow from organisational context through evidence-backed recommendations.

```


