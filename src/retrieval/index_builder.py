import os
from typing import List, Dict
from src.extraction.schema import MedicalGuideline
from src.knowledge.knowledge_ingestor import KnowledgeIngestor

# A shared repository of official medical guidelines for RAG query search
GUIDELINE_CORPUS = [
    {
        "id": "GL-001",
        "source_name": "ACC/AHA",
        "guideline_name": "2019 Guidelines on Primary Prevention of Cardiovascular Disease",
        "text_snippet": "Initiation of statin therapy is recommended for primary prevention of cardiovascular disease in adults aged 40-75 years with LDL cholesterol levels >= 190 mg/dL or when 10-year atherosclerotic cardiovascular disease (ASCVD) risk is >= 7.5%. Target LDL-C reduction is >= 50% for high intensity statins.",
        "evidence_tier": "Tier 1: Strong Evidence",
        "year": 2019,
        "url": "https://www.ahajournals.org/doi/10.1161/CIR.0000000000000678"
    },
    {
        "id": "GL-002",
        "source_name": "NICE",
        "guideline_name": "Cardiovascular disease: risk assessment and reduction, incl lipid modification",
        "text_snippet": "Offer atorvastatin 20 mg for primary prevention of CVD to people who have a 10% or greater 10-year risk of developing CVD. Measure total cholesterol, HDL cholesterol, non-HDL cholesterol & triglycerides before starting statin therapy, checking within 3 months.",
        "evidence_tier": "Tier 1: Strong Evidence",
        "year": 2023,
        "url": "https://www.nice.org.uk/guidance/ng238"
    },
    {
        "id": "GL-003",
        "source_name": "ADA",
        "guideline_name": "Standards of Care in Diabetes—2024",
        "text_snippet": "An HbA1c level of >= 6.5% is diagnostic of Diabetes Mellitus. Patients with HbA1c >= 8.0% indicate sub-optimal glycemic control and require treatment escalation with Metformin or combined insulin therapies. Routine self-monitoring and annual microvascular screen are necessary.",
        "evidence_tier": "Tier 1: Strong Evidence",
        "year": 2024,
        "url": "https://diabetesjournals.org/care/issue/47/Supplement_1"
    },
    {
        "id": "GL-004",
        "source_name": "AACE",
        "guideline_name": "Guidelines for Management of Growth Hormone/Lipids",
        "text_snippet": "In patients with high-risk triglycerides levels (>200 mg/dL), lifestyle interventions including reduced carbohydrates, sugar intake, and enhanced aerobic exercise are key baselines. Fibrates may be considered for severe hypertriglyceridemia (>500 mg/dL) to prevent acute pancreatitis.",
        "evidence_tier": "Tier 2: Moderate Evidence",
        "year": 2021,
        "url": "https://www.aace.com/clinical-guidelines"
    },
    {
        "id": "GL-005",
        "source_name": "WHO",
        "guideline_name": "Guidelines on Syphilis and Infectious Diseases Diagnosis",
        "text_snippet": "An elevated White Blood Cell (WBC) count (>11.0 x10^3/uL) suggests infection or systemic inflammation, requiring assessment of clinical symptoms (fever, localizing pain, pulmonary cough). Culture and differential counts represent standard diagnostic procedures.",
        "evidence_tier": "Tier 2: Moderate Evidence",
        "year": 2020,
        "url": "https://www.who.int/publications/i/item/9789241549714"
    },
    {
        "id": "GL-006",
        "source_name": "CDC",
        "guideline_name": "Guidance on Infectious Pyrexia & Leukocytosis Management",
        "text_snippet": "Leukocytosis (WBC counts > 11.0 x10^3/uL) combined with high core temperature (>38.0 C) suggests bacterial or viral response. Broad-spectrum empiric antibiotics may be indicated only secondary to culture confirmation to reduce antimicrobial resistance.",
        "evidence_tier": "Tier 2: Moderate Evidence",
        "year": 2022,
        "url": "https://www.cdc.gov/guidelines"
    },
    {
        "id": "GL-007",
        "source_name": "NICE",
        "guideline_name": "Type 1 & 2 Diabetes in Adults: Diagnosis and Treatment Guidelines",
        "text_snippet": "If fasting blood glucose is >= 126 mg/dL or random glucose >= 200 mg/dL in symptomatic patients, diagnose diabetes. Lifestyle therapy consisting of caloric deficits, portion controls, and regular weight monitoring should accompany initial pharmacotherapy.",
        "evidence_tier": "Tier 1: Strong Evidence",
        "year": 2023,
        "url": "https://www.nice.org.uk/guidance/ng28"
    },
    {
        "id": "GL-008",
        "source_name": "AHA",
        "guideline_name": "Primary Classification of Blood Pressure Stages",
        "text_snippet": "Stage 2 Hypertension is defined as Systolic Blood Pressure >= 140 mmHg or Diastolic Blood Pressure >= 90 mmHg. Treatment requires combinations of pharmacological agents (ACE inhibitors, ARBs, Calcium Channel blockers) and severe dietary sodium limits.",
        "evidence_tier": "Tier 1: Strong Evidence",
        "year": 2017,
        "url": "https://www.ahajournals.org/doi/10.1161/HYP.0000000000000065"
    }
]

class GuidelineIndexBuilder:
    def __init__(self):
        self.ingestor = KnowledgeIngestor()
        self.corpus = GUIDELINE_CORPUS + self._load_source_documents()

    def _load_source_documents(self) -> List[dict]:
        documents = []
        for item in self.ingestor.load_corpus():
            title = item.get("title") or item.get("source") or item.get("id") or "Medical Knowledge"
            source_name = item.get("source") or title
            text_snippet = item.get("text") or item.get("text_snippet") or ""
            category = item.get("category", "general_guideline")
            version = item.get("version") or str(item.get("metadata", {}).get("version", "2024"))
            documents.append({
                "id": item.get("id") or f"knowledge-{len(documents)+1}",
                "source_name": source_name,
                "guideline_name": title,
                "text_snippet": text_snippet,
                "category": category,
                "source_type": item.get("source_type", "guideline"),
                "version": version,
                "metadata": item.get("metadata", {}),
                "evidence_tier": item.get("metadata", {}).get("evidence_tier", "Tier 2: Moderate Evidence"),
                "year": int(version[:4]) if version and version[:4].isdigit() else 2024,
                "url": item.get("metadata", {}).get("url"),
            })
        return documents

    def get_all_guidelines(self) -> List[MedicalGuideline]:
        return [MedicalGuideline(**item) for item in self.corpus]
