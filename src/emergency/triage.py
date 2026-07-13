from typing import List

EMERGENCY_KEYWORDS = [
    "chest pain",
    "difficulty breathing",
    "shortness of breath",
    "unconscious",
    "severe bleeding",
    "stroke",
    "heart attack",
    "suicidal",
    "convulsions",
    "fainting",
    "confusion",
    "severe weakness",
    "choking",
    "not breathing",
    "unable to breathe"
]

SYMPTOM_KEYWORDS = [
    "fever",
    "cough",
    "sore throat",
    "headache",
    "nausea",
    "vomiting",
    "diarrhea",
    "dizziness",
    "fatigue",
    "rash",
    "swelling",
    "pain",
    "burning",
    "cold",
    "flu"
]


class EmergencyTriage:
    def is_emergency(self, message: str) -> bool:
        normalized = message.lower()
        return any(keyword in normalized for keyword in EMERGENCY_KEYWORDS)

    def is_symptom(self, message: str) -> bool:
        normalized = message.lower()
        return any(keyword in normalized for keyword in SYMPTOM_KEYWORDS)

    def build_emergency_response(self) -> str:
        return (
            "This sounds like a potential medical emergency. Please seek immediate medical attention or call your local emergency number if you experience severe chest pain, difficulty breathing, fainting, confusion, or uncontrolled bleeding."
        )

    def build_symptom_guidance(self) -> str:
        return (
            "I'm sorry you're feeling unwell. Fever and other symptoms can come from common infections such as a cold, flu, or COVID-19, or from other conditions."
            " Please tell me:\n"
            "- your age\n"
            "- how long you've had the symptom\n"
            "- whether you measured your temperature\n"
            "- whether you have cough, sore throat, body aches, nausea, vomiting, or difficulty breathing\n"
            "Meanwhile, rest, stay hydrated, and seek medical attention if symptoms worsen or persist more than 3 days."
        )
