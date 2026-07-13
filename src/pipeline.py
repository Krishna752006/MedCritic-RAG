import os
from typing import List
from src.ingestion.pdf_parser import PDFParser
from src.ingestion.ocr_engine import OCREngine
from src.ingestion.vlm_extractor import VLMExtractor
from src.extraction.ner_pipeline import NERPipeline
from src.extraction.normalizer import MedicalNormalizer
from src.retrieval.retriever import RetrievalManager
from src.verification.critic_verifier import CriticVerifier
from src.verification.confidence import ConfidenceCalibrator
from src.generation.clinical_gen import ClinicalGenerator
from src.generation.medical_analysis import MedicalAnalysisGenerator
from src.generation.patient_gen import PatientGenerator
from src.generation.multilingual import MultilingualService
from src.navigation.urgency_detector import UrgencyDetector
from src.navigation.specialty_router import SpecialtyRouter
from src.navigation.facility_finder import FacilityFinder
from src.extraction.schema import DiagnosticReportAnalysis


class MedCriticPipeline:
    def __init__(self):
        self.pdf_parser = PDFParser()
        self.ocr_engine = OCREngine()
        self.vlm_extractor = VLMExtractor()
        self.ner = NERPipeline()
        self.normalizer = MedicalNormalizer()
        self.retrieval_manager = RetrievalManager()
        self.verifier = CriticVerifier()
        self.urgency_detector = UrgencyDetector()
        self.specialty_router = SpecialtyRouter()
        self.facility_finder = FacilityFinder()
        self.clinical_gen = ClinicalGenerator()
        self.analysis_gen = MedicalAnalysisGenerator()
        self.patient_gen = PatientGenerator()
        self.translation_service = MultilingualService()

    def process_report(self, file_path: str, lang: str = "en") -> DiagnosticReportAnalysis:
        """
        Executes the end-to-end MedCritic-RAG++ pipeline.

        The system supports both production-grade modules when installed and a simulated
        evaluation mode by falling back to synthetic extraction and retrieval outputs.
        """
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Input file not found: {file_path}")

        file_name = os.path.basename(file_path).lower()
        is_image = file_name.endswith(('.png', '.jpg', '.jpeg', '.tiff'))

        if is_image:
            extracted_text = self.ocr_engine.perform_ocr(file_path)
            visual_metadata = self.vlm_extractor.extract_visual_elements(file_path)
        else:
            extracted_text = self.pdf_parser.extract_text(file_path)
            visual_metadata = {
                "document_type": "Medical Report",
                "has_graphs": False,
                "source": "PDF/Text" if file_name.endswith('.pdf') else "Text Fallback"
            }

        findings = self.ner.extract_findings(extracted_text)
        findings = self.normalizer.normalize(findings)

        query_terms = [f.name for f in findings if f.status.lower() not in ["normal", "optimal"]]
        if not query_terms:
            query_terms = [f.name for f in findings]

        query_text = " ".join(query_terms) if query_terms else "Medical report clinical assessment"
        guidelines, retrieval_context = self.retrieval_manager.retrieve(query_text, top_k=4)

        verifications = self.verifier.verify_findings(findings, guidelines)
        calibrated_confidence = ConfidenceCalibrator.calculate(verifications)

        analysis = self.analysis_gen.analyze(findings, guidelines)
        clinical_summary = self.translation_service.translate_report(analysis["clinical_summary"], lang)
        patient_explanation = self.translation_service.translate_report(analysis["patient_explanation"], lang)

        urgency_info = self.urgency_detector.evaluate_urgency(findings)
        specialty_info = self.specialty_router.route_specialty(findings)
        facility_list = self.facility_finder.find_nearest(specialty_info["specialty"])

        return DiagnosticReportAnalysis(
            raw_extracted_text=extracted_text,
            findings=findings,
            guidelines_retrieved=guidelines,
            verifications=verifications,
            clinical_summary=clinical_summary,
            patient_explanation=patient_explanation,
            urgency_level=urgency_info["urgency_level"],
            urgency_reasoning=urgency_info["reasoning"],
            recommended_specialty=specialty_info["specialty"],
            recommended_specialty_reasoning=specialty_info["reasoning"],
            nearby_facilities=facility_list,
            abnormal_findings=analysis["abnormal_findings"],
            possible_conditions=analysis["possible_conditions"],
            follow_up_recommendations=analysis["follow_up_recommendations"],
            lifestyle_recommendations=analysis["lifestyle_recommendations"],
            risk_analysis=analysis["risk_analysis"],
            urgency_classification=analysis["urgency_classification"],
            red_flags=analysis["red_flags"],
            recommended_specialists=analysis["recommended_specialists"],
            source_attribution=analysis["source_attribution"],
            language=lang,
            calibrated_confidence=calibrated_confidence,
            retrieval_context=retrieval_context,
        )
