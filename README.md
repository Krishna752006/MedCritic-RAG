# MedCritic-RAG++: Multimodal Verified Clinical Decision Support

MedCritic-RAG++ is a multimodal, verified Retrieval-Augmented Generation (RAG) framework designed to interpret uploaded medical reports (PDF/images), resolve clinical findings to standardized terminologies (SNOMED-CT, LOINC, ICD-10), perform verifiable NLI-based fact-checking against official health guidelines (WHO, NICE, CDC, ADA, ACC/AHA), calibrate generation confidence, and execute intelligent care navigation routing.

This repository implements a production-grade backend using **FastAPI** and **SQLAlchemy** (PostgreSQL), a hybrid neural/lexical retrieval engine, a clinical claim-verification layer (based on the CRITIC framework), and a React-based single-page dashboard.

---

## 📂 Repository Structure & Component Map

The project is structured with a clean separation of concerns. The FastAPI server handles request routing and session state, while the domain logic is encapsulated in the `src/` core library.

```
medcritic-rag-plus-plus/
├── api/
│   └── main.py                     # Entry point for the FastAPI server (imports backend/app/main.py)
├── backend/
│   ├── app/
│   │   ├── api/                    # FastAPI route definitions
│   │   │   ├── auth.py             # Auth status placeholder
│   │   │   ├── chat.py             # Session-based chat endpoints
│   │   │   ├── documents.py        # Chat document upload and extraction endpoints
│   │   │   ├── health.py           # API health status check
│   │   │   ├── medical.py          # Standalone medical term normalization
│   │   │   └── reports.py          # Report analysis, benchmarking, and graph endpoints
│   │   ├── config/
│   │   │   ├── logging.py          # Centralized application logging configurations
│   │   │   └── settings.py         # App configuration settings (.env parser)
│   │   ├── database/               # Relational persistence layer
│   │   │   ├── base.py             # Declarative SQLAlchemy base class
│   │   │   ├── models.py           # Database models (User, Chat, Message, Document, etc.)
│   │   │   └── session.py          # Session factory and get_db() dependency
│   │   ├── llm/
│   │   │   └── generator.py        # LLM query building interface
│   │   ├── medical/
│   │   │   └── clinical_parser.py  # Regex/rule-based clinical document parses
│   │   ├── migrations/             # Alembic database migrations history
│   │   ├── models/
│   │   │   └── schemas.py          # Pydantic request/response validation schemas
│   │   ├── rag/
│   │   │   └── retriever.py        # Adapter mapping database retrieval services
│   │   ├── services/               # Internal business logic adapters
│   │   │   ├── chat_service.py     # Relays chat workflows to core agents
│   │   │   ├── document_service.py # Document DB record management
│   │   │   ├── entity_service.py   # Standardizes raw texts to codings
│   │   │   ├── report_service.py   # Report ingestion coordinator
│   │   │   ├── retrieval_service.py# Query search connector
│   │   │   ├── urgency_service.py  # Navigation routing interface
│   │   │   └── verification_service.py # Claim checks orchestrator
│   │   └── workflows/              # Multi-service operations
│   │       ├── chat_workflow.py    # Manages chats list/history modifications
│   │       ├── comparison_workflow.py # Handles document comparisons
│   │       └── report_workflow.py  # Wraps report analysis entry points
│   └── migrations/                 # Alembic configuration scripts
├── data/
│   ├── datasets/                   # Raw databases placeholders
│   ├── documents/                  # Storage directory for uploaded documents
│   ├── knowledge/                  # RAG indexing databases
│   │   ├── sources/                # Downloaded medical knowledge text files (Asthma, Stroke, etc.)
│   │   └── bm25_corpus.json        # Chunky BM25 tokenized medical corpus
│   └── temp/                       # Local file processing buffer
├── frontend/                       # Vite + React dashboard portal
│   ├── public/                     # Static assets
│   ├── src/
│   │   ├── assets/                 # Styling images and fonts
│   │   ├── App.tsx                 # Core single-page dashboard application
│   │   ├── AppNew.tsx              # Alternate design template
│   │   ├── index.css               # Global Tailwind directives
│   │   └── main.tsx                # React virtual DOM mounter
│   ├── index.html                  # HTML entry point
│   ├── package.json                # Frontend NPM dependencies
│   ├── tsconfig.json               # TypeScript options config
│   └── vite.config.ts              # Vite configuration
├── scripts/                        # Administrative CLI commands
│   ├── ingest_medical_datasets.py  # Parses PubMedQA/MedQuAD datasets into BM25
│   └── train_medical_knowledge.py  # Seed local documents from Wikipedia
├── src/                            # Core domain library
│   ├── chat/
│   │   ├── clinical_agent.py       # Orchestrates chat intent, memory, and advice
│   │   ├── conversation_memory.py  # Manages chat sessions history and triage states
│   │   ├── medical_chat.py         # Main chat engine with intent classification and triage loop
│   │   └── task_router.py          # Resolves message intents to active workflows
│   ├── datasets/
│   │   └── ingest.py               # MedQuAD / PubMedQA parser logic
│   ├── emergency/
│   │   └── triage.py               # Evaluates acute emergency keywords
│   ├── evaluation/
│   │   └── benchmark_tracker.py    # Tracks latency, calibration error, and accuracy
│   ├── extraction/
│   │   ├── ner_pipeline.py         # Named Entity Recognition (Regex + spaCy)
│   │   ├── normalizer.py           # Standard mappings to LOINC, SNOMED-CT, and ICD-10
│   │   └── schema.py               # Shared Pydantic data schemas (MedicalFinding, etc.)
│   ├── generation/
│   │   ├── clinical_gen.py         # Professional physician summaries builder
│   │   ├── medical_analysis.py     # Inferential logic (conditions, red flags, specialists)
│   │   ├── multilingual.py         # Glossary translating headings to ES, HI, TE
│   │   └── patient_gen.py          # Layperson patient glossary translator
│   ├── ingestion/
│   │   ├── ocr_engine.py           # PaddleOCR image extraction wrapper
│   │   ├── pdf_parser.py           # PyMuPDF PDF parser
│   │   └── vlm_extractor.py        # BioMedCLIP multimodal visual layout parsing
│   ├── knowledge/
│   │   └── knowledge_ingestor.py   # Chunks, categorizes, and indexes source guidelines
│   ├── llm/
│   │   └── llm_service.py          # Model interface loader (flan-t5-small)
│   ├── navigation/
│   │   ├── facility_finder.py      # Nearest clinic facility listings database
│   │   ├── specialty_router.py     # Specialty clinic routing counts
│   │   └── urgency_detector.py     # Diagnostic severity assessment
│   ├── pipeline.py                 # End-to-end report interpreter orchestrator
│   ├── retrieval/
│   │   ├── context_builder.py      # Cleans and formats RAG context snippets
│   │   ├── dense_retriever.py      # SentenceTransformers + FAISS similarity index
│   │   ├── reranker.py             # Neural Cross-Encoder query-snippet relevance re-scoring
│   │   ├── retriever.py            # Combines dense, sparse, and reranking retrieves
│   │   └── sparse_retriever.py     # BM25 lexical similarity search
│   └── verification/
│       ├── confidence.py           # NLI flag confidence percentage calibrator
│       ├── critic_verifier.py      # Aligns values to clinical guideline thresholds
│       ├── evidence_tier.py        # Quality weights (Tier 1 vs Tier 2 vs Tier 3)
│       └── evidence_verifier.py    # Source authority evaluation (Star rankings)
├── Dockerfile                      # Backend container configuration
├── docker-compose.yml              # All-in-one local compose deployment spec
├── requirements.txt                # Python package list
└── alembic.ini                     # Alembic migration configuration
```

---

## ⚡ The End-to-End Report Analysis Pipeline

When a medical report is uploaded, it is routed through the **MedCriticPipeline** (`src/pipeline.py`), which coordinates several processing modules sequentially:

```mermaid
graph TD
    A[Scanned PDF or Image] --> B{File Extension?}
    B -- Image/Scanned PDF --> C[PaddleOCR / VLM Extractor]
    B -- Native PDF --> D[PyMuPDF / PDFParser]
    C --> E[Raw Text & Visual Metadata]
    D --> E
    E --> F[NER Pipeline: regex + spaCy]
    F --> G[Medical Normalizer: UMLS mappings to SNOMED/LOINC/ICD-10]
    G --> H[Hybrid Retrieval Engine: Dense FAISS + Sparse BM25 Guidelines]
    H --> I[Cross-Encoder Reranker: ms-marco MiniLM]
    I --> J[CRITIC Verifier: rule check & verification flags]
    J --> K[Conformal Confidence Calibrator]
    K --> L[Medical Analysis: Infer conditions, red flags, specialists]
    L --> M[Dual-Register Generation: Clinical Provider Summary + Patient Plain Language Cards]
    M --> N[Care Router: Specialty routing + Nearest Hospital facility matching]
    N --> O[Multilingual Service: Hindi / Spanish / Telugu translation]
    O --> P[DiagnosticReportAnalysis Pydantic Payload]
```

### 1. Ingestion (`src/ingestion/`)
* **`pdf_parser.py`**: Extracts text from native PDFs using `PyMuPDF` (`fitz`).
* **`ocr_engine.py`**: Uses `PaddleOCR` to parse scanned images.
* **`vlm_extractor.py`**: Simulates/loads `BioMedCLIP` (`ViT-B-32-harmonic`) to detect visual elements (bar charts, layout structure, red accents, signatures).
* *Note: Graceful fallbacks are coded to simulate OCR outputs based on filename cues if hardware/libraries are missing.*

### 2. Entity Extraction & Normalization (`src/extraction/`)
* **`ner_pipeline.py`**: Runs a rule-based regex parsing engine alongside spaCy (`en_core_web_sm`) to isolate clinical tests, metrics, values, units, and status flags.
* **`normalizer.py`**: Links entities to standardized clinical codes:
  * **LOINC**: For laboratory measurements (e.g., Fasting Glucose: `1558-6`).
  * **SNOMED-CT**: For clinical terms and anatomy (e.g., Hypertension: `38341003`).
  * **ICD-10**: For diagnosis classification (e.g., Type 2 Diabetes: `E11.9`).

### 3. Hybrid RAG Retrieval (`src/retrieval/`)
* **Sparse Retrieval (`sparse_retriever.py`)**: Token-based keyword search using `rank_bm25` (`BM25Okapi`).
* **Dense Retrieval (`dense_retriever.py`)**: Semantic search using `sentence-transformers` (`all-MiniLM-L6-v2`) and a `FAISS` inner product index (`IndexFlatIP`).
* **Hybrid Reranking (`reranker.py`)**: Dedupes results and runs a neural Cross-Encoder (`cross-encoder/ms-marco-MiniLM-L-6-v2`) to score query-snippet relevance. Scores are boosted based on an **Evidence Tier Weight** (Tier 1: Global Health Authority, Tier 2: Specialist Society Consensus, Tier 3: General Clinical Trial).
* *Note: Both retrievers and the reranker include algorithmic fallback systems (lexical intersection, Reciprocal Rank Fusion) if the deep learning packages are unavailable.*

### 4. Verification & Confidence Calibration (`src/verification/`)
* **`critic_verifier.py`**: Checks extracted numerical values against guideline-defined thresholds (e.g., checks if LDL $\ge 190\text{ mg/dL}$ triggers statins under ACC/AHA, HbA1c $\ge 6.5\%$ diagnostic of diabetes under ADA, WBC $> 11.0\times 10^3/\mu\text{L}$ shows leukocytosis). Claims are flagged as **Verified**, **Contradicted**, or **Unverified**.
* **`evidence_verifier.py`**: Maps source names to authority tiers:
  * **Tier 1 (5 Stars ★★★★★)**: Global Health Authorities (WHO, CDC, NICE, FDA, EMA).
  * **Tier 2 (4 Stars ★★★★)**: Specialist Societies (ADA, ACC, AHA, ESC, AACE).
  * **Tier 3 (3 Stars ★★★)**: Peer-reviewed Journals (PubMed, Lancet, JAMA).
  * **Other (2 Stars ★★)**: General Clinical Trials/Medical Wikis.
* **`confidence.py`**: Calculates a calibrated confidence score:
  $$\text{Confidence} = 0.10 + 0.89 \times \frac{\sum (\text{NLI Weight} \times \text{Strength Score})}{\text{Total Claims}}$$
  *(Verified = Weight 1.0, Unverified = Weight 0.4, Contradicted = Weight 0.0)*

### 5. Medical Analysis & Dual-Register Generation (`src/generation/`)
* **`medical_analysis.py`**: Infers likely conditions, detects cardiorespiratory and neurological red flags, classifies urgency, and determines recommended specialists.
* **`clinical_gen.py`**: Produces a technical summary detailing ontologies, code mappings, and provider-specific action plans.
* **`patient_gen.py`**: Generates a plain-language glossary explaining what each test value means and outlines layperson lifestyle recommendations.
* **`multilingual.py`**: Uses a translation glossary to convert headings into Hindi (`hi`), Spanish (`es`), or Telugu (`te`).

### 6. Care Navigation (`src/navigation/`)
* **`urgency_detector.py`**: Determines urgency level (Emergency, Urgent, Routine) using clinical rule sets.
* **`specialty_router.py`**: Routes cases to Endocrinology, Cardiology, Hematology, or Primary Care by summing weighted parameters.
* **`facility_finder.py`**: Matches routed specialties with a local simulated database of emergency hospitals, specialist centers, and primary clinics.

---

## 💬 The Step-by-Step Symptom Triage Chat System

The conversation assistant is managed by the **ClinicalAgent** (`src/chat/clinical_agent.py`), coordinating memory, intent classification, and clinical guidance:

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant Agent as ClinicalAgent
    participant Memory as ConversationMemory
    participant Router as ClinicalTaskRouter
    participant Chat as MedicalChatService
    participant LLM as LLMService

    User->>Agent: "I have a fever"
    Agent->>Memory: add_message("user", "I have a fever")
    Agent->>Router: route(session_id, "I have a fever")
    Router->>Chat: detect_intent("I have a fever")
    Note over Chat: Intent classified as "symptom"
    Chat->>Memory: get_metadata(session_id)
    Note over Chat: Missing triage data:<br/>duration, temp, age, gender, allergies...
    Chat->>Memory: activate_triage(session_id)
    Chat->>Memory: mark_asked("symptom_duration")
    Chat-->>User: "How long have you had this fever?"
    
    User->>Agent: "Since yesterday"
    Note over Agent, Chat: Loop runs to collect missing metadata...
    
    Note over Chat: All triage metadata collected!
    Chat->>Memory: deactivate_triage(session_id)
    Chat->>Chat: retrieve relevant guidelines (BM25)
    Chat->>LLM: generate(prompt + guidelines + patient_context)
    LLM-->>Chat: plain-text clinical guidance
    Chat-->>User: Formatted Triage Header + Risk Level + Guidance + Evidence Block
```

### 1. Intent Detection (9 Core Intents)
The chat service classifies the user's input into one of nine intents to determine the workflow:
1. `greeting`: Welcomes the user and lists capabilities.
2. `goodbye`: Close chat session and show disclaimer.
3. `emergency`: Triggers the immediate emergency first-aid protocols.
4. `report_upload`: Instructs the user to navigate to the interpreter tab.
5. `symptom`: Initiates the structured triage questionnaire.
6. `follow_up`: Continues the triage metadata collection loop.
7. `disease_info`: Fetches clinical knowledge on a specific disease.
8. `medicine_info`: Retrieves dosage, side effects, and precautions for drugs.
9. `small_talk` / `casual`: Friendly out-of-scope conversation handler.

### 2. Conversational Triage Metadata Collection
To ensure clinical safety, if the user describes a symptom, the system activates a triage loop. It checks `ConversationMemory` to see if any of the following fields are missing, asking for them one by one without repeating questions:
* Main symptom
* Symptom duration
* Temperature (if a fever is mentioned)
* Patient age
* Biological sex (Male/Female)
* Pregnancy status (if female)
* Food or drug allergies
* Pre-existing medical conditions

Once all triage data is collected, it calculates the patient's risk level, retrieves guidelines via RAG, queries `google/flan-t5-small` (via `LLMService`), and appends an **Evidence Block** (source attribution, ranking stars, confidence, and hallucination risk classification) to the output.

---

## 🗄️ Database & Persistence Layer

The backend uses **SQLAlchemy** to interface with a PostgreSQL database, storing session state and document records.

* **Database Connection**: Defaults to `postgresql+psycopg://postgres:postgres@localhost:5432/medcritic`.
* **Migrations**: Managed via **Alembic**. The configurations are set up in `alembic.ini` and historical migrations are stored under `backend/app/migrations/`.

### Entity-Relationship Schema

```mermaid
erDiagram
    USERS {
        uuid id PK
        string email
        datetime created_at
    }
    CHATS {
        uuid id PK
        uuid user_id FK
        string title
        text summary
        jsonb metadata_json
        datetime created_at
        datetime updated_at
    }
    MESSAGES {
        uuid id PK
        uuid chat_id FK
        string role
        text content
        jsonb metadata_json
        datetime created_at
    }
    DOCUMENTS {
        uuid id PK
        uuid chat_id FK
        string filename
        string content_type
        string storage_path
        text extracted_text
        jsonb metadata_json
        datetime created_at
    }
    DOCUMENT_CHUNKS {
        uuid id PK
        uuid document_id FK
        integer chunk_index
        text text
        string embedding_id
        jsonb metadata_json
        datetime created_at
    }
    ANALYSIS_RESULTS {
        uuid id PK
        uuid document_id FK
        jsonb result_json
        integer confidence
        datetime created_at
    }
    KNOWLEDGE_SOURCES {
        uuid id PK
        string source_name
        string title
        string url
        string version
        jsonb metadata_json
        datetime created_at
    }

    USERS ||--o{ CHATS : "owns"
    CHATS ||--o{ MESSAGES : "contains"
    CHATS ||--o{ DOCUMENTS : "attaches"
    DOCUMENTS ||--o{ DOCUMENT_CHUNKS : "split into"
    DOCUMENTS ||--o{ ANALYSIS_RESULTS : "analyzed as"
```

---

## 🖥️ Frontend Overview

The client-side dashboard is built with **Vite, React, TypeScript, and TailwindCSS**, serving as a dashboard.

* **Development Port**: Port `5173` or production preview port `4173`.
* **Backend Connection**: Queries the FastAPI backend at `http://localhost:8000`.
* **Core Views (Tabs)**:
  1. **Report Interpreter**: Provides a file upload interface. Once uploaded, it animates through pipeline stages (OCR -> entity parsing -> RAG retrieval -> verification), rendering the final dual-register output, code maps, and maps/facilities.
  2. **Patient Profile**: Renders a card displaying the current patient's attributes synchronized from reports and triage sessions.
  3. **Symptom Triage Chat**: A chat interface featuring:
     * **Speech Recognition**: Voice-to-text input using the browser's Web Speech API (`SpeechRecognition`).
     * **Speech Synthesis**: Text-to-speech output using `SpeechSynthesisUtterance`.
     * **Explainability Sidebar**: Shows the current intent, reasoning path, source, star ranking, and NLI verification score for the latest response.
  4. **Knowledge Graph**: Renders a dynamic relationship graph linking diseases, symptoms, medications, specialists, and clinics.
  5. **Research Benchmarks**: Renders evaluation statistics (e.g., Claims Verified, Hallucination Rate, Conformal Calibration P-value, and latency distribution charts).

---

## 🚀 Installation & Setup

### Method 1: Local Native Setup

#### 1. Setup Backend
1. Create and activate a Python virtual environment:
   ```bash
   python -m venv myenv
   myenv\Scripts\activate   # Windows
   source myenv/bin/activate # macOS/Linux
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Download the spaCy language model:
   ```bash
   python -m spacy download en_core_web_sm
   ```
4. Build the local BM25 guideline database:
   ```bash
   python scripts/train_medical_knowledge.py
   ```
5. Run the FastAPI development server:
   ```bash
   uvicorn api.main:app --reload --port 8000
   ```
   *The interactive API documentation is available at `http://localhost:8000/api/v1/docs`.*

#### 2. Setup Frontend
1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install npm packages:
   ```bash
   npm install
   ```
3. Run the development server:
   ```bash
   npm run dev
   ```
   *Open `http://localhost:5173` in your browser.*

---

### Method 2: Docker Compose

You can spin up the entire stack (FastAPI Backend + React Frontend + PostgreSQL Database) in containers:

1. Build and start the services:
   ```bash
   docker-compose up --build
   ```
2. The services will be accessible at:
   * **FastAPI Backend**: `http://localhost:8000`
   * **React Dashboard**: `http://localhost:4173`

---

## 📑 References

* **CRITIC-RAG: Verified Medical Reasoning** — *doi:10.1109/JBHI.2026.3687666*
* **Self-BioRAG: Medical Self-Reflection** — *arXiv:2401.15269*
* **MKRAG: Medical Knowledge RAG** — *arXiv:2309.16035*
* **Rethinking Retrieval-Augmented Medicine** — *arXiv:2511.06738*
