from typing import List
from src.extraction.schema import MedicalFinding

class UrgencyDetector:
    def evaluate_urgency(self, findings: List[MedicalFinding]) -> dict:
        """
        Determines the clinical urgency of medical findings.
        Returns:
          {
            "urgency_level": "Emergency" | "Urgent" | "Routine",
            "reasoning": str
          }
        """
        severity = "Routine"
        reasons = []

        for f in findings:
            if not f.value:
                continue

            name_lower = f.name.lower()
            try:
                val = float(f.value)
                
                # Check HbA1c diabetic markers
                if "hba1c" in name_lower:
                    if val >= 8.5:
                        severity = "Urgent"
                        reasons.append(f"HbA1c level ({val}%) shows uncontrolled hyperglycemia.")
                    elif val > 10.0:
                        severity = "Emergency"
                        reasons.append(f"Critical HbA1c ({val}%) risk of diabetic emergencies.")
                
                # Check Cholesterol and Lipids
                elif "cholesterol" in name_lower or "ldl" in name_lower:
                    if val >= 250.0 or val >= 190.0:
                        if severity != "Emergency":
                            severity = "Urgent"
                        reasons.append(f"Highly elevated cholesterol levels ({val} mg/dL) posing cardiovascular risks.")
                        
                # Check White Blood Cells (Infection flags)
                elif "wbc" in name_lower or "white blood cell" in name_lower:
                    if val > 14.0 or val < 3.0:
                        severity = "Urgent"
                        reasons.append(f"Abnormal leukocyte count ({val} x10^3/uL) suggesting systemic response.")
                        if val > 18.0:
                            severity = "Emergency"
                            reasons.append(f"Critical Leucocytosis ({val} x10^3/uL) suggesting acute infection.")
                            
            except ValueError:
                # Text assessment for status tags
                if f.status.lower() == "critical" or "critical" in f.description.lower():
                    severity = "Emergency"
                    reasons.append(f"Critical tag on finding '{f.name}'.")
                elif f.status.lower() in ["abnormal", "elevated"] and severity == "Routine":
                    severity = "Urgent"
                    reasons.append(f"Elevated status tag on finding '{f.name}'.")

        if not reasons:
            return {
                "urgency_level": "Routine",
                "reasoning": "All findings appear within standard ranges or represent mild baseline elevations. Schedule routine reviews."
            }

        # Resolve urgency
        final_level = "Routine"
        if "Emergency" in [r for r in reasons] or any("Emergency" in r or "Critical" in r for r in reasons):
            final_level = "Emergency"
        elif any("hyperglycemia" in r or "elevated" in r or "abnormal" in r or "count" in r for r in reasons):
            final_level = "Urgent"
        else:
            final_level = "Routine"
            
        if final_level == "Emergency":
            reasoning_summary = f"EMERGENCY ATTENTION REQUIRED: {', '.join(reasons)} Please consult emergency room immediately."
        elif final_level == "Urgent":
            reasoning_summary = f"URGENT REVIEW ADVISED: {', '.join(reasons)} Schedule clinician review within 24-48 hours."
        else:
            reasoning_summary = f"ROUTINE SUGGESTION: {', '.join(reasons)}"

        return {
            "urgency_level": final_level,
            "reasoning": reasoning_summary
        }
