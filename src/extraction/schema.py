from pydantic import BaseModel, Field
from typing import List, Optional

class MedicalFinding(BaseModel):
    name: str = Field(..., description="Extract medical entity, symptom, or lab test")
    value: Optional[str] = Field(None, description="Extracted measurement or finding value")
    unit: Optional[str] = Field(None, description="Measurement unit (e.g. mg/dL, g/L)")
    reference_range: Optional[str] = Field(None, description="Normal biological range")
    status: str = Field("normal", description="Status details (e.g., normal, abnormal, elevated, critical)")
    snomed_code: Optional[str] = Field(None, description="SNOMED-CT Clinical Terminology identifier")
    loinc_code: Optional[str] = Field(None, description="LOINC code for laboratory measurements")
    icd10_code: Optional[str] = Field(None, description="ICD-10 classification of diseases/problems")
    category: Optional[str] = Field(None, description="Entity category such as disease, symptom, medication, lab_test, or vital_sign")
    description: Optional[str] = Field(None, description="Patient-friendly contextual explanation of findings")

class MedicalGuideline(BaseModel):
    id: str
    source_name: str = Field(..., description="E.g., WHO, NICE, CDC, ACC/AHA")
    guideline_name: str
    text_snippet: str
    category: Optional[str] = Field("disease_guideline", description="Knowledge category such as disease_guideline, drug_information, lab_reference, emergency_criteria")
    source_type: Optional[str] = Field("guideline", description="Source type such as guideline, monograph, reference")
    version: Optional[str] = Field(None, description="Source document version or guideline year")
    metadata: dict = Field(default_factory=dict, description="Extended structured metadata for the guideline source")
    evidence_tier: str = Field("Tier 2: Moderate", description="WHO/NICE classification (Tier 1: Strong, Tier 2: Moderate, Tier 3: Weak/Observational)")
    year: int
    url: Optional[str] = None

class VerificationEvidence(BaseModel):
    claim: str
    status: str = Field("Verified", description="Verified, Contradicted, or Unverified")
    strength_score: float = Field(..., description="Evaluated matching logic score [0, 1.0]")
    supporting_guideline_id: Optional[str] = None
    verification_reasoning: str = Field(..., description="Step-by-step logic checking verification status")

class CareFacility(BaseModel):
    name: str
    type: str = Field("General Hospital", description="Specialty, General, Emergency Care")
    distance_km: float
    address: str
    contact: str
    specialty_match: bool = True

class DiagnosticReportAnalysis(BaseModel):
    raw_extracted_text: str
    findings: List[MedicalFinding] = []
    guidelines_retrieved: List[MedicalGuideline] = []
    verifications: List[VerificationEvidence] = []
    clinical_summary: str = Field(..., description="For medical professionals")
    patient_explanation: str = Field(..., description="In layperson-accessible language")
    urgency_level: str = Field("Routine", description="Routine, Urgent, or Emergency")
    urgency_reasoning: str
    recommended_specialty: str
    recommended_specialty_reasoning: str
    nearby_facilities: List[CareFacility] = []
    abnormal_findings: List[str] = []
    possible_conditions: List[str] = []
    follow_up_recommendations: List[str] = []
    lifestyle_recommendations: List[str] = []
    risk_analysis: str = Field("Low risk", description="Overall risk analysis")
    urgency_classification: str = Field("Routine", description="Urgency classification for medical priority")
    red_flags: List[str] = []
    recommended_specialists: List[str] = []
    source_attribution: List[str] = []
    language: str = "en"
    calibrated_confidence: float = Field(0.95, description="Confidence metric based on NLI verification checks")
    retrieval_context: List[dict] = []
