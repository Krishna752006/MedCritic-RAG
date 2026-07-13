from typing import List
from src.extraction.schema import MedicalFinding

class SpecialtyRouter:
    def route_specialty(self, findings: List[MedicalFinding]) -> dict:
        """
        Maps clinical codes to appropriate clinical departments.
        """
        if not findings:
            return {
                "specialty": "General Medicine / Primary Care",
                "reasoning": "No abnormal findings detected. Routine wellness checks handled by General Practice."
            }

        counts = {
            "Cardiology": 0,
            "Endocrinology": 0,
            "Infectious Diseases / Hematology": 0,
            "Primary Care": 0
        }

        for f in findings:
            name_lower = f.name.lower()
            if "cholesterol" in name_lower or "ldl" in name_lower or "triglyceride" in name_lower or "blood pressure" in name_lower:
                counts["Cardiology"] += 2
            elif "hba1c" in name_lower or "glucose" in name_lower or "tsh" in name_lower:
                counts["Endocrinology"] += 2
            elif "wbc" in name_lower or "white blood cell" in name_lower or "platelet" in name_lower or "red blood cell" in name_lower:
                counts["Infectious Diseases / Hematology"] += 2
            else:
                counts["Primary Care"] += 1

        # Sort and select best route
        routed = max(counts, key=counts.get)
        
        # Build explanation
        if routed == "Cardiology":
            reasoning = "Target parameters track lipids (LDL, Triglycerides) and cardiovascular metrics (Blood Pressure). Cardio-metabolic therapy is recommended."
        elif routed == "Endocrinology":
            reasoning = "Findings suggest glycemic imbalances (HbA1c, Fasting Glucose) or thyroid adjustments (TSH). Requires metabolic evaluation by an Endocrinologist."
        elif routed == "Infectious Diseases / Hematology":
            reasoning = "Active variations in White Blood Cells or platelets indicate possible systemic immune or bone-marrow response. Requires hematology or general infectious screening."
        else:
            reasoning = "Constitutional measurements suggest general clinical indicators. Recommended consultation with Primary Care physician."

        return {
            "specialty": routed,
            "reasoning": reasoning
        }
