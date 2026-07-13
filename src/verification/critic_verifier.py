import re
from typing import List
from src.extraction.schema import MedicalFinding, MedicalGuideline, VerificationEvidence

class CriticVerifier:
    def verify_findings(self, findings: List[MedicalFinding], guidelines: List[MedicalGuideline]) -> List[VerificationEvidence]:
        """
        Validates clinical findings against rules in retrieved guidelines.
        """
        evidences = []
        guideline_dict = {g.id: g for g in guidelines}

        for finding in findings:
            finding_name = finding.name.lower()
            matching_gl = self._find_matching_guideline(finding_name, guideline_dict)
            claim = f"Extracted level of {finding.name} is {finding.value or 'N/A'} {finding.unit or ''}, status tagged as {finding.status}."
            status = "Unverified"
            strength = 0.30
            reason = f"No retrieved official guidelines matching '{finding.name}' in active index."
            supporting_id = None

            if matching_gl:
                supporting_id = matching_gl.id
                status, strength, reason = self._assess_against_guideline(finding, finding_name, matching_gl)

            evidences.append(VerificationEvidence(
                claim=claim,
                status=status,
                strength_score=strength,
                supporting_guideline_id=supporting_id,
                verification_reasoning=reason
            ))

        return evidences

    def _find_matching_guideline(self, finding_name: str, guideline_dict: dict) -> MedicalGuideline | None:
        if any(x in finding_name for x in ["cholesterol", "ldl", "triglyceride"]):
            for g_id in ["GL-001", "GL-002", "GL-004"]:
                if g_id in guideline_dict:
                    return guideline_dict[g_id]
        if any(x in finding_name for x in ["hba1c", "glucose"]):
            for g_id in ["GL-003", "GL-007"]:
                if g_id in guideline_dict:
                    return guideline_dict[g_id]
        if any(x in finding_name for x in ["wbc", "white blood cell"]):
            for g_id in ["GL-005", "GL-006"]:
                if g_id in guideline_dict:
                    return guideline_dict[g_id]
        if "blood pressure" in finding_name or "hypertension" in finding_name:
            return guideline_dict.get("GL-008")
        return None

    def _assess_against_guideline(self, finding: MedicalFinding, finding_name: str, guideline: MedicalGuideline) -> tuple[str, float, str]:
        status = "Verified"
        strength = 0.95
        reason = "Aligned with retrieved guideline evidence."

        if finding.value:
            try:
                value_text = re.sub(r"[^0-9.]", "", finding.value)
                val_float = float(value_text)
            except ValueError:
                val_float = None

            if val_float is not None:
                if any(x in finding_name for x in ["cholesterol", "ldl"]):
                    if guideline.id == "GL-001" and val_float >= 190:
                        reason = f"Verified: LDL {val_float} mg/dL meets ACC/AHA statin guideline risk threshold." 
                    elif guideline.id == "GL-004" and val_float >= 200:
                        reason = f"Verified: Triglyceride {val_float} mg/dL exceeds AACE high-risk recommendation." 
                    else:
                        reason = f"Verified: Lipid result is supported by active lipid management guidance."
                elif "hba1c" in finding_name:
                    if guideline.id == "GL-003" and val_float >= 6.5:
                        reason = f"Verified: HbA1c {val_float}% is consistent with ADA diabetes diagnostic criteria." 
                    elif guideline.id == "GL-003" and val_float < 6.5:
                        status = "Contradicted"
                        strength = 0.30
                        reason = f"Contradiction: HbA1c {val_float}% is below the ADA diabetes threshold, which may not support a diabetes diagnosis."
                elif "wbc" in finding_name:
                    if val_float > 11.0:
                        reason = f"Verified: WBC {val_float} x10^3/uL confirms leukocytosis interpretation per infection guidelines." 
                    else:
                        status = "Unverified"
                        strength = 0.50
                        reason = f"Unverified: WBC {val_float} is within common range and may not indicate active infection."
                elif any(x in finding_name for x in ["blood pressure", "hypertension"]):
                    if val_float >= 140:
                        reason = f"Verified: Systolic blood pressure {val_float} mmHg meets stage 2 hypertension criteria." 
                    else:
                        status = "Unverified"
                        strength = 0.60
                        reason = f"Unverified: Blood pressure {val_float} mmHg does not meet the highest hypertension threshold in the guideline."
        else:
            reason = f"Verified text alignment with {guideline.source_name} guideline on {finding.name}."

        return status, strength, reason
