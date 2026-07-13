# MedCritic-RAG++: Multimodal Verified Clinical Decision Support

MedCritic-RAG++ is a multimodal verified Retrieval-Augmented Generation (RAG) framework designed to interpret uploaded medical reports (PDF/images), resolve clinical findings to standardized ontologies (UMLS, SNOMED-CT, LOINC, ICD-10), perform verifiable fact-checking against official health guidelines (WHO, NICE, CDC, ADA, ACC/AHA), calibrate generation confidence, and map care navigation routing.

## Project Structure
```
medcritic-rag-plus-plus/
├── api/
│   └── main.py               # FastAPI server endpoints
├── data/
│   └── temp/                 # Ingestion processing buffer (gitignored)
├── frontend/
│   ├── src/
│   │   ├── App.tsx           # React Dashboard Portal
│   │   └── index.css         # Tailwind & global styling directives
│   ├── index.html            # Web entry and fonts load
│   └── package.json          # Node dependencies
├── src/
│   ├── ingestion/
│   │   ├── ocr_engine.py     # OCR text extraction
│   │   ├── pdf_parser.py     # PyMuPDF text reader
│   │   └── vlm_extractor.py  # Page layouts VLM extraction
│   ├── extraction/
│   │   ├── ner_pipeline.py   # SpaCy clinical named entity recognizer
│   │   ├── normalizer.py     # SNOMED/LOINC/ICD-10 clinical map service
│   │   └── schema.py         # Shared Pydantic data schemas
│   ├── retrieval/
│   │   ├── index_builder.py  # Guidelines database corpus initialization
│   │   ├── dense_retriever.py# FAISS vector retriever
│   │   ├── sparse_retriever.py# BM25 token matching retriever
│   │   └── reranker.py       # Cross-Encoder hybrid relevance ranker
│   ├── verification/
│   │   ├── critic_verifier.py# CRITIC claim-evidence verifier NLI
│   │   ├── confidence.py     # Confidence level percentage calibrator
│   │   └── evidence_tier.py  # NICE/WHO guidelines authority tiers
│   ├── generation/
│   │   ├── clinical_gen.py   # Technical professional synthesis generator
│   │   ├── patient_gen.py    # Patient-friendly explanation generator
│   │   └── multilingual.py   # Language translation translation module
│   ├── navigation/
│   │   ├── urgency_detector.py# Alarm limits assessments
│   │   ├── specialty_router.py# Disease -> routing medical specialties
│   │   └── facility_finder.py# Location coordinates mapping
│   └── pipeline.py           # End-to-end framework orchestrator
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Getting Started

### Method 1: Local Native Setup

#### 1. Setup Backend
Activate a virtual environment and load dependencies:
```bash
# Install packages
pip install -r requirements.txt

# Download default spaCy language weights
python -m spacy download en_core_web_sm

# Launch FastAPI dev server
uvicorn api.main:app --reload --port 8000
```

#### 2. Setup Frontend
Run the Vite development server:
```bash
cd frontend
npm install
npm run dev
```

### Method 2: Docker Compose (All Services)
Simply run Docker Compose in the root directory:
```bash
docker-compose up --build
```
This launches the backend service at `http://localhost:8000`.

### Medical Chat Assistant
To build the medical knowledge base and enable the backend chat model:
```bash
python scripts/train_medical_knowledge.py
```
Then start the backend and use the frontend chat tab to submit follow-up clinical questions.

## Clinical AI Platform Architecture
- Frontend React app connects to a FastAPI backend.
- Backend routes user messages through intent detection and task routing.
- Medical queries use a hybrid RAG + evidence verification + LLM response pipeline.
- Report uploads are handled by OCR, entity extraction, retrieval, and clinical explanation modules.
- Emergency and symptom messages are detected before retrieval to provide safe triage guidance.
- Knowledge data is stored locally in `data/knowledge`, with training via `scripts/train_medical_knowledge.py`.

## Features
- **Visual OCR & Layout Parsing:** Resolves scanned documents and tabular columns.
- **Ontology Alignment & Code Maps:** Resolves entities to LOINC, SNOMED, and ICD-10.
- **CRITIC Verification Loop:** Automatically corroborates or flags claims against official NICE, WHO, and CDC guidelines.
- **Dual register generation:** Simultaneously formats technical physician summaries and layperson plain-language cards.
- **Intelligent Referrals:** Maps patient diagnosis triggers directly to target clinics and emergency levels.

## Gap Analysis & Differentiation
- **GAP-01:** Lack of Medical Report Interpretation
  - CRITIC-RAG: Answers only generic questions
  - MedCritic-RAG++: OCR + table parsing to clinical detail
- **GAP-02:** Lack of Multimodal Document Understanding
  - CRITIC-RAG: Text-only matching
  - MedCritic-RAG++: VLM layout and chart reasoning
- **GAP-03:** No Patient-Friendly Explanations
  - CRITIC-RAG: Complex medical jargon
  - MedCritic-RAG++: Dual-register patient summaries
- **GAP-04:** No Confidence Estimation
  - CRITIC-RAG: High risk of hallucinated statistics
  - MedCritic-RAG++: NLI-calibrated conformal confidence
- **GAP-05:** No Clinical Navigation
  - CRITIC-RAG: Leaves patients stranded
  - MedCritic-RAG++: Specialty routing and GIS facilities
- **GAP-06:** Limited Personalization/History
  - CRITIC-RAG: Single prompt interactions
  - MedCritic-RAG++: Contextual history indexing
- **GAP-07:** Limited Scanner Document Support
  - CRITIC-RAG: Pre-parsed text expectation
  - MedCritic-RAG++: PaddleOCR engine built-in

## Comparative Capability Matrix
| Dimension | CRITIC-RAG (Baseline) | MedCritic-RAG++ (Ours) |
|---|---|---|
| Document Input | Raw Text / Text QA | Multimodal PDFs & OCR Images |
| Retrieval Pipeline | Dense Vector Search | Weighted Dense + Sparse BM25 + Rerank |
| Verification Engine | CRITIC-RAG NLI Logic | Evidence-strength leveling (WHO/NICE) |
| Safety Calibration | Yes/No claims check | Conformal calibration percentage |
| Target Registers | Clinical summary only | Dual: Clinical summary + patient glossary |
| Clinical Routing | None | Urgency grading & specialty routing |

## Pipeline Architecture
[Scanned PDF/Image] ➔ [PaddleOCR / fitz Extraction] ➔ [Clinical NER (UMLS mappings)] ➔ [Hybrid Retrieval Engine (Weighted Vector FAISS + BM25 Guidelines index)] ➔ [ColBERT/Cross-Encoder Rerankings] ➔ [CRITIC Verification Loop Check] ➔ [Conformal Confidence Calibrator] ➔ [Dual Register Generators] ➔ [Physician clinical register output] ➔ [Patient-friendly layperson summary] ➔ [GIS facility care router]

## Research Roadmap
- Month 1-2: OCR & document parsers
- Month 3-4: Biomedical NER & normalization
- Month 5-6: Dense FAISS & BM25 retrieval
- Month 7-8: CRITIC verifier & calibration
- Month 9-10: Dual generation & routing engines
- Month 11-12: Evaluation & paper writing

## References
- CRITIC-RAG: Verified Medical Reasoning — doi:10.1109/JBHI.2026.3687666
- Self-BioRAG: Medical Self-Reflection — doi:arXiv:2401.15269
- MKRAG: Medical Knowledge RAG — doi:arXiv:2309.16035
- Rethinking Retrieval-Augmented Medicine — doi:arXiv:2511.06738
