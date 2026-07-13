from typing import List, Dict


class ClinicalDecisionSupport:
    """Basic clinical recommendation and reasoning layer for the AI agent."""

    def assess(self, question: str, sources: List[Dict[str, str]]) -> Dict[str, str]:
        normalized = question.lower()
        recommendation = "Consider clinical review or follow-up if symptoms persist."
        reasoning = "This assistant provides high-level guidance and does not replace clinical judgment."
        specialist = "General physician"

        emergency_terms = ["emergency", "chest pain", "difficulty breathing", "unconscious", "stroke", "severe bleeding"]
        cardiology_terms = ["heart", "hypertension", "cholesterol", "ldl", "angina", "arrhythmia"]
        endocrinology_terms = ["diabetes", "hba1c", "glucose", "insulin", "thyroid", "metformin"]
        nephrology_terms = ["kidney", "renal", "creatinine", "bun", "egfr"]

        if any(keyword in normalized for keyword in emergency_terms):
            recommendation = "Seek immediate emergency care or call your local emergency number."
            reasoning = "The query contains potential red flags that require urgent medical evaluation."
            specialist = "Emergency care"
        elif any(keyword in normalized for keyword in cardiology_terms):
            recommendation = "Follow up with a cardiologist for detailed cardiovascular evaluation."
            reasoning = "The query indicates cardiovascular risk factors or symptoms that benefit from specialist review."
            specialist = "Cardiologist"
        elif any(keyword in normalized for keyword in endocrinology_terms):
            recommendation = "Consult an endocrinologist for metabolic and hormonal assessment."
            reasoning = "The query involves diabetes or endocrine regulation, which is best managed by a specialist."
            specialist = "Endocrinologist"
        elif any(keyword in normalized for keyword in nephrology_terms):
            recommendation = "See a nephrologist if kidney function or blood chemistry is involved."
            reasoning = "The query refers to renal or metabolic markers that may need specialist evaluation."
            specialist = "Nephrologist"
        elif any(keyword in normalized for keyword in ["fever", "cough", "headache", "pain", "nausea", "dizziness"]):
            recommendation = "Monitor symptoms closely and consult a clinician if they worsen or persist beyond a few days."
            reasoning = "Symptom-based queries are best managed by trending clinical status and seeking professional evaluation."
        elif sources:
            recommendation = "Review the referenced medical sources and discuss the findings with your healthcare provider."
            reasoning = "The response is grounded in retrieved evidence and should be interpreted alongside clinical context."

        return {
            "recommendation": recommendation,
            "reasoning": reasoning,
            "specialist": specialist,
        }
