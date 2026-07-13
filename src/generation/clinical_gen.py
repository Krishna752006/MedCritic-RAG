from typing import List
from src.extraction.schema import MedicalFinding, MedicalGuideline

class ClinicalGenerator:
    def generate_summary(self, findings: List[MedicalFinding], guidelines: List[MedicalGuideline]) -> str:
        """
        Generates high-precision, technical medical documentation.
        """
        if not findings:
            return "No significant clinical findings extracted from document analysis."

        summary_lines = [
            "CLINICAL INTERPRETATION REPORT (PROVIDER REGISTER)",
            "--------------------------------------------------",
            f"Active Findings Count: {len(findings)}",
            "Extracted Clinical Values & Ontologies:"
        ]

        for idx, f in enumerate(findings, 1):
            unit_str = f" {f.unit}" if f.unit else ""
            summary_lines.append(
                f"  {idx}. {f.name}: {f.value}{unit_str} | Status: [{f.status.upper()}] "
                f"(LOINC: {f.loinc_code}, SNOMED: {f.snomed_code}, ICD-10: {f.icd10_code})"
            )

        summary_lines.append("\nReference Guidelines Retained for Clinical Rationale:")
        for idx, g in enumerate(guidelines, 1):
            summary_lines.append(
                f"  - [{g.source_name} ({g.year})] {g.guideline_name} | Evidence: {g.evidence_tier}"
            )

        summary_lines.append(
            "\nRecommended Physician Action Plan: Evaluate critical values against current medication logs. "
            "Coordinate appropriate diagnostic overlays and confirm with targeted standard evaluations."
        )

        return "\n".join(summary_lines)
