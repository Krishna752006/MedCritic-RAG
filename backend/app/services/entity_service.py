from src.extraction.ner_pipeline import NERPipeline
from src.extraction.normalizer import MedicalNormalizer
from src.extraction.schema import MedicalFinding

from backend.app.medical.clinical_parser import ClinicalParser


class EntityService:
    def __init__(self):
        self.ner = NERPipeline()
        self.normalizer = MedicalNormalizer()
        self.clinical_parser = ClinicalParser()

    def extract_findings(self, text: str):
        parsed = self.clinical_parser.parse(text)
        findings = parsed["findings"] or self.ner.extract_findings(text)
        entity_findings = self._entities_to_findings(parsed["entities"])
        return self.normalizer.normalize(self._dedupe_findings([*findings, *entity_findings]))

    def understand(self, text: str) -> dict:
        parsed = self.clinical_parser.parse(text)
        findings = parsed["findings"] or self.ner.extract_findings(text)
        all_findings = self.normalizer.normalize(
            self._dedupe_findings([*findings, *self._entities_to_findings(parsed["entities"])])
        )
        return {
            "report_type": parsed["report_type"],
            "entities": parsed["entities"],
            "findings": all_findings,
            "lab_tests": [finding for finding in all_findings if finding.category == "lab_test" or (finding.value and not self._is_vital(finding.name))],
            "vital_signs": [finding for finding in all_findings if self._is_vital(finding.name) or finding.category == "vital_sign"],
            "normalized_codes": [
                {
                    "name": finding.name,
                    "loinc_code": finding.loinc_code,
                    "snomed_code": finding.snomed_code,
                    "icd10_code": finding.icd10_code,
                }
                for finding in all_findings
            ],
        }

    def _entities_to_findings(self, entities: dict) -> list[MedicalFinding]:
        findings = []
        for bucket in ("diseases", "symptoms", "medications"):
            for entity in entities.get(bucket, []):
                findings.append(
                    MedicalFinding(
                        name=entity["name"],
                        category=entity["category"],
                        status="mentioned",
                        description=f"Mentioned {entity['category']}: {entity['name']}.",
                    )
                )
        return findings

    def _dedupe_findings(self, findings: list[MedicalFinding]) -> list[MedicalFinding]:
        deduped = []
        seen = set()
        for finding in findings:
            key = (finding.name.lower(), finding.value, finding.unit)
            if key in seen:
                continue
            seen.add(key)
            deduped.append(finding)
        return deduped

    def _is_vital(self, name: str) -> bool:
        return name.lower() in {
            "blood pressure",
            "heart rate",
            "respiratory rate",
            "temperature",
            "oxygen saturation",
        }
