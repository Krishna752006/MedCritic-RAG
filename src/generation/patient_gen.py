from typing import List
from src.extraction.schema import MedicalFinding

class PatientGenerator:
    def generate_explanation(self, findings: List[MedicalFinding]) -> str:
        """
        Translates medical codes and findings into layperson-accessible guidelines.
        """
        if not findings:
            return "Your clinical report has been processed and no out-of-range findings were flagged. This is excellent!"

        abnormal_findings = [f for f in findings if f.status.lower() not in ["normal", "optimal"]]
        
        explanation_lines = [
            "PATIENT GLOSSARY & PERSONAL HEALTH INSIGHTS",
            "===========================================",
            "Your health provider has received your report. Below is a breakdown of your key findings in plain language:\n"
        ]

        for f in findings:
            status_text = "Out of Range" if f.status.lower() not in ["normal", "optimal"] else "Normal"
            explanation_lines.append(f"• {f.name}: {f.value} {f.unit or ''} ({status_text})")
            explanation_lines.append(f"  What this means: {f.description}\n")

        if abnormal_findings:
            explanation_lines.append("HEALTH ACTIONS TO DISCUSS")
            explanation_lines.append("-------------------------")
            explanation_lines.append("1. Dietary & Lifestyle Support: Review your nutritional plans relative to these findings.")
            explanation_lines.append("2. Consult with a specialist: We recommend scheduling an appointment to review these results.")
            explanation_lines.append("3. Keep active: Try to stick to moderate exercise if cleared by your GP.")
        else:
            explanation_lines.append("Conclusion: Keep up the healthy habits! Maintain routine annual health checks.")

        return "\n".join(explanation_lines)
