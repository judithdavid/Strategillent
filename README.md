![Strategillent CI](https://github.com/judithdavid/Strategillent/actions/workflows/ci.yml/badge.svg)

# Strategillent

## AI Transformation Strategy Intelligence

Strategillent is a full-stack AI transformation intelligence application. It combines an organisation profile with industry-applicable research evidence to generate strategic issue analysis and transformation opportunities. It also includes deterministic opportunity prioritisation, proposed pilot initiatives, an intelligence Q&A interface, web-research ingestion, and a separate semantic document-retrieval API.

The application is demonstrated primarily with **FinNova**, a fictional digital payments and consumer-lending organisation.

> Strategillent is a demonstration and decision-support application. Generated analysis and recommendations require human review; evidence-reference validation does not establish that a source semantically proves a claim.

## Core workflow

```text
Organisation Profile
        +
Industry-Applicable Research Evidence
        |
        v
Strategic Issue Analysis (LLM)
        |
        v
Transformation Opportunity Generation (LLM)
        |
        v
Deterministic Priority Scoring
        |
        v
Proposed Pilot Initiatives
        |
        v
Persisted Results and Frontend Review
```

The application keeps fictional organisation context separate from external research records so that organisation assumptions are not presented as independently sourced facts.

## Demonstration data

The repository includes structured seed data for three demonstration areas:

| Industry pack | Seed evidence records |
|---|---:|
| FinTech (FinNova) | 32 |
| EdTech | 4 |
| Healthcare | 4 |
| **Total** | **40** |

The seed data also includes **14 transformation dimensions** with industry applicability metadata and an industry registry containing canonical names and aliases.

Research evidence records contain fields such as claim, supporting evidence, source details, publication date, tags, industry applicability, relevance, and confidence. The application uses industry and evidence-domain selection to avoid using unrelated seed evidence in the main intelligence-generation workflow.

FinNova is fictional. Its organisation profile is demonstration input; the external research records are separate source material.

## Features

### 1. Organisation management

- Create, view, and update organisation profiles through the application.
- Store industry, business model, markets, customers, employees, products, goals, challenges, processes, technology, and constraints.
- Persist organisation records and related analysis data in SQLite through SQLAlchemy.

### 2. Evidence-aware intelligence generation

The main intelligence workflow:

1. Loads the organisation's industry-applicable evidence.
2. Selects transformation dimensions applicable to that industry.
3. Filters evidence for each dimension using its configured evidence domains.
4. Calls the LLM issue analyser for dimensions with relevant evidence.
5. Generates transformation opportunities using the issue, organisation context, dimension, and filtered evidence.
6. Calculates deterministic opportunity priorities.
7. Creates proposed pilot initiative records and persists the analysis run.

The issue analyser and opportunity generator use Ollama with Llama 3.2 when LLM generation is enabled. They request structured JSON output and validate it against Pydantic schemas. A configurable deterministic fallback is available when LLM generation fails.

### 3. LLM configuration and output validation

- Configurable Ollama base URL, model, temperature, context window, prediction limit, and request timeouts.
- JSON-constrained generation for structured issue and opportunity outputs.
- Pydantic schema validation for generated data.
- Bounded context construction with configurable character and evidence-record limits.
- Evidence-reference validation to check that generated citation IDs belong to the evidence supplied to that generation step.
- Prompt instructions distinguish organisation-provided context from external evidence and ask the model to state uncertainty or missing information.

**Important:** citation validation checks reference integrity, not semantic entailment. A valid evidence ID does not prove that the cited source supports the generated statement.

### 4. Deterministic opportunity prioritisation

Opportunity priority is calculated in application code rather than delegated entirely to the LLM:

```text
Priority Score =
    0.35 × Business Impact
  + 0.20 × Feasibility
  + 0.20 × Urgency
  + 0.15 × Strategic Alignment
  + 0.10 × Evidence Confidence
```

The application stores the resulting priority score and rank for each opportunity. The weights are explicit and can be reviewed independently of the generated narrative.

### 5. Evidence retrieval

Strategillent contains two distinct retrieval paths:

**Main intelligence and Q&A paths**
- The intelligence-generation workflow selects SQL-persisted evidence by organisation industry and transformation-dimension evidence domains.
- The Q&A service currently uses keyword matching over SQL-persisted evidence, then supplies the selected records and organisation context to the answer generator.

**Separate semantic retrieval API**
- Uses a local persistent Qdrant collection.
- Uses FastEmbed with `BAAI/bge-small-en-v1.5` embeddings.
- Chunks evidence records and uploaded documents while retaining source and industry metadata.
- Supports semantic search with optional industry and domain filters.
- Combines semantic similarity, lexical overlap, evidence relevance, and evidence confidence for final ranking.

The semantic retrieval API is a separate capability; it is **not currently the retrieval implementation used by the main intelligence Q&A service**. Evidence indexing into Qdrant is triggered through the indexing endpoint rather than automatically whenever a SQL evidence record is created.

The semantic ranking weights are:

| Component | Weight |
|---|---:|
| Semantic similarity | 0.60 |
| Lexical overlap | 0.20 |
| Evidence relevance | 0.10 |
| Evidence confidence | 0.10 |

### 6. Document ingestion

The semantic retrieval API accepts documents with these extensions:

- PDF
- DOCX
- TXT
- HTML / HTM
- CSV
- Markdown / MD

The ingestion flow extracts text, splits it into overlapping chunks, creates embeddings, and stores the chunks and metadata in Qdrant. Scanned PDFs that require OCR are not covered by the current extraction implementation.

### 7. External web research

- Integrates with the Tavily Search API.
- Accepts a query, industry, domain, and maximum result count.
- Stores returned search content as research-source and evidence records.
- Uses a stable URL-derived external identifier to recognise previously stored URLs.
- Marks imported web results as `unverified`.

Web-search results are candidate source material, not independently verified facts. They should be reviewed for credibility, relevance, and applicability before being relied on. Newly stored SQL evidence is not automatically indexed into Qdrant.

### 8. Frontend

The React and TypeScript interface includes:

- Dashboard
- Organisation profile
- Intelligence analysis
- Opportunities
- Evidence
- Ask Intelligence

The frontend communicates with the FastAPI backend through REST endpoints.

## Application architecture

```text
┌───────────────────────────────────────────────┐
│             React + TypeScript UI             │
│ Dashboard | Organisation | Intelligence       │
│ Opportunities | Evidence | Ask Intelligence   │
└───────────────────────┬───────────────────────┘
                        │ REST
                        v
┌───────────────────────────────────────────────┐
│                  FastAPI                      │
│ Organisation | Research | Intelligence        │
│ Questions | Web Research | Semantic Retrieval │
└───────────────┬───────────────────┬───────────┘
                │                   │
                v                   v
┌────────────────────────┐  ┌───────────────────────┐
│ Main AI Workflow       │  │ Semantic Retrieval    │
│                        │  │                       │
│ Ollama / Llama 3.2     │  │ FastEmbed             │
│ Issue Analysis         │  │ BGE-small-en-v1.5     │
│ Opportunity Generation│  │ Qdrant                │
│ Structured Validation │  │ Chunking and Ranking  │
└────────────┬───────────┘  └───────────────────────┘
             │
             v
┌───────────────────────────────────────────────┐
│           SQLite + SQLAlchemy                 │
│ Organisations | Evidence | Sources            │
│ Dimensions | Issues | Opportunities           │
│ Initiatives | Analysis Runs                   │
└───────────────────────────────────────────────┘

External research:
Tavily Search → SQL Research Sources / Evidence
```

## Technology stack

### Frontend
- React
- TypeScript
- Vite
- React Router
- Lucide React

### Backend
- Python
- FastAPI
- SQLAlchemy
- SQLite
- Pydantic
- Pydantic Settings

### LLM and AI
- Ollama
- Llama 3.2
- Structured JSON generation
- Pydantic output validation
- Prompt engineering

### Retrieval and document processing
- Qdrant
- FastEmbed
- `BAAI/bge-small-en-v1.5`
- PDF extraction with pypdf
- DOCX extraction with python-docx
- BeautifulSoup for HTML extraction

### External research
- Tavily Search API
- Requests

### Testing and CI
- Pytest
- GitHub Actions (backend test workflow)

## Repository structure

```text
Strategillent/
├── .github/
│   └── workflows/
│       └── ci.yml
├── backend/
│   ├── app/
│   │   ├── ai/             # LLM client, prompts, context and output validation
│   │   ├── api/            # FastAPI route modules
│   │   ├── core/           # Settings, database and logging
│   │   ├── models/         # SQLAlchemy models
│   │   ├── retrieval/      # Qdrant, embeddings, chunking and ranking
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   ├── seed/           # Seed-data loader
│   │   ├── services/       # Business logic and workflows
│   │   ├── utils/
│   │   └── main.py
│   ├── scripts/
│   │   └── seed.py
│   ├── tests/
│   └── requirements.txt
├── data/
│   └── seed/
│       ├── evidence.json
│       ├── edtech_evidence.json
│       ├── healthcare_evidence.json
│       ├── industry_registry.json
│       ├── organisation.json
│       └── transformation_dimensions.json
├── frontend/
│   ├── src/
│   │   ├── context/
│   │   ├── hooks/
│   │   ├── pages/
│   │   ├── services/
│   │   └── types/
│   ├── package.json
│   └── vite.config.ts
├── research/
│   ├── external_evidence.json
│   ├── finnova_context.json
│   ├── research_notes.md
│   └── transformation_dimensions.json
├── README.md
└── .gitignore
```

## Prerequisites

Install:

- Python 3.12+
- Node.js and npm
- Ollama
- Git

Qdrant runs locally through the Qdrant client. The first embedding-model use may download the configured FastEmbed model.

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/judithdavid/Strategillent.git
cd Strategillent
```

### 2. Start the local LLM

Install Ollama, then download and start Llama 3.2:

```bash
ollama run llama3.2
```

Keep Ollama available while using AI-dependent application features.

### 3. Configure the backend

Open a terminal in the repository root:

```bash
cd backend
```

Create and activate a virtual environment:

```bash
python -m venv .venv
```

Windows:

```powershell
.venv\Scripts\activate
```

macOS / Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Optional configuration can be placed in `backend/.env`. For example:

```dotenv
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
INTELLIGENCE_USE_LLM=true
INTELLIGENCE_ALLOW_DETERMINISTIC_FALLBACK=true
TAVILY_API_KEY=
```

`TAVILY_API_KEY` is required only for the web-research endpoint. Do not commit `.env` files or API keys.

### 4. Initialise and seed the database

From the `backend/` directory:

```bash
python scripts/seed.py
```

This initialises the database and loads the organisation, evidence, industry, and transformation-dimension seed data.

### 5. Start the backend

From the `backend/` directory:

```bash
uvicorn app.main:app --reload
```

- API: http://127.0.0.1:8000
- Interactive API documentation: http://127.0.0.1:8000/docs
- Health check: http://127.0.0.1:8000/health

### 6. Start the frontend

Open a second terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the local URL printed by Vite, normally:

```text
http://localhost:5173
```

To run the frontend TypeScript check and production build:

```bash
npm run build
```

## API overview

The main API route groups are:

| Route prefix | Purpose |
|---|---|
| `/api/organisations` | Organisation records and profiles |
| `/api/research` | Research sources, evidence, domains, and web research |
| `/api/intelligence` | Run and retrieve intelligence analysis |
| `/api/questions` | Ask questions about an organisation |
| `/api/semantic_retrieval` | Index evidence, ingest documents, and perform semantic search |

Useful endpoints include:

```text
POST /api/intelligence/{organisation_id}/run
GET  /api/intelligence/{organisation_id}
POST /api/questions/{organisation_id}
POST /api/research/web-search
POST /api/semantic_retrieval/index-evidence
POST /api/semantic_retrieval/documents
POST /api/semantic_retrieval/search
```

See `/docs` for request and response schemas.

## Testing

Backend tests are in:

```text
backend/tests/
```

Run them from the `backend/` directory:

```bash
pytest -v
```

The repository contains 17 backend test modules and 71 test functions covering areas including:

- Organisation APIs and seed loading
- Industry resolution and industry-specific evidence selection
- Research APIs
- Intelligence generation and industry isolation
- Intelligence workflow integration
- Opportunity prioritisation
- Question answering
- Web research and evidence persistence
- Semantic retrieval helpers and search

GitHub Actions runs the backend test workflow on pushes and pull requests to `main` and `master`. The workflow installs backend requirements, initialises and seeds a CI database, and runs Pytest. The current workflow does not run a frontend build or TypeScript check.

## Traceability and validation

Strategillent records evidence IDs associated with generated issues and opportunities. The structured generation path validates output against Pydantic schemas and checks that cited evidence IDs were included in the generation context.

These checks improve structural consistency and reference integrity. They do not automatically establish source credibility, factual correctness, or semantic support for every generated claim. Human review remains necessary.

## Current limitations and scope

- FinNova is the primary demonstration scenario; the additional industry seed packs exercise industry-aware data selection but do not establish production readiness for those sectors.
- The main Q&A service currently uses SQL keyword matching and does not call the Qdrant semantic-search service.
- Qdrant semantic retrieval is exposed through a separate API. Evidence must be indexed into Qdrant before it can be found there; SQL evidence creation does not automatically update the vector collection.
- Web-search results are stored as unverified evidence candidates and require review.
- Evidence citation validation checks whether referenced IDs were supplied; it does not prove that a cited source supports a claim.
- Uploaded-document ingestion extracts text but does not perform OCR on scanned PDFs.
- The application does not currently provide authentication, role-based access control, or multi-user data isolation.
- SQLite and local Qdrant storage are intended for local demonstration and development, not a production deployment architecture.
- Generated analysis and pilot proposals are decision-support outputs and require human review.
- The strategy-generation module is not part of the currently wired main intelligence API workflow.

## Design principles

- Separate organisation context from external research.
- Filter the main analysis by industry and transformation evidence domains.
- Prefer structured model output over free-form generated records.
- Validate model output and evidence references.
- Keep opportunity priority scoring deterministic and inspectable.
- Persist analysis records and their relationships.
- Keep local LLM execution and retrieval components configurable.
- Make limitations and uncertainty visible rather than manufacturing unsupported conclusions.
