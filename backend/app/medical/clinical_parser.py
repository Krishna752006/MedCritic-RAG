import re
from dataclasses import dataclass

from src.extraction.schema import MedicalFinding


@dataclass(frozen=True)
class ClinicalPattern:
    name: str
    aliases: tuple[str, ...]
    category: str


class ClinicalParser:
    REPORT_HINTS = {
        "cbc": ("complete blood count", "cbc", "hemoglobin", "platelet", "white blood cell", "wbc"),
        "lipid_profile": ("lipid", "cholesterol", "hdl", "ldl", "triglycerides"),
        "diabetes": ("hba1c", "glucose", "diabetic", "fasting plasma glucose", "oral glucose"),
        "kidney_function": ("creatinine", "urea", "bun", "egfr", "uric acid", "kidney"),
        "liver_function": ("bilirubin", "sgpt", "sgot", "alt", "ast", "alkaline phosphatase", "liver"),
        "ecg": ("ecg", "ekg", "sinus rhythm", "st elevation", "qrs", "qt interval"),
        "radiology": ("x-ray", "xray", "ct scan", "mri", "ultrasound", "impression", "radiology"),
    }

    ENTITY_PATTERNS = (
        ClinicalPattern("Diabetes mellitus", ("diabetes", "diabetic", "hyperglycemia"), "disease"),
        ClinicalPattern("Hypertension", ("hypertension", "high blood pressure"), "disease"),
        ClinicalPattern("Chronic kidney disease", ("chronic kidney disease", "ckd"), "disease"),
        ClinicalPattern("Asthma", ("asthma", "wheezing"), "disease"),
        ClinicalPattern("Myocardial infarction", ("myocardial infarction", "heart attack"), "disease"),
        ClinicalPattern("Fever", ("fever", "pyrexia", "high temperature"), "symptom"),
        ClinicalPattern("Cough", ("cough",), "symptom"),
        ClinicalPattern("Chest pain", ("chest pain", "chest tightness"), "symptom"),
        ClinicalPattern("Shortness of breath", ("shortness of breath", "dyspnea", "difficulty breathing"), "symptom"),
        ClinicalPattern("Polyuria", ("polyuria",), "symptom"),
        ClinicalPattern("Polydipsia", ("polydipsia",), "symptom"),
        ClinicalPattern("Metformin", ("metformin",), "medication"),
        ClinicalPattern("Atorvastatin", ("atorvastatin", "lipitor"), "medication"),
        ClinicalPattern("Aspirin", ("aspirin",), "medication"),
        ClinicalPattern("Paracetamol", ("paracetamol", "acetaminophen"), "medication"),
        ClinicalPattern("Ibuprofen", ("ibuprofen",), "medication"),
        ClinicalPattern("Lisinopril", ("lisinopril",), "medication"),
        ClinicalPattern("Albuterol", ("albuterol", "salbutamol"), "medication"),
    )

    LAB_PATTERNS = {
        "Hemoglobin": ("hemoglobin", "hb"),
        "White Blood Cell Count": ("white blood cell count", "wbc"),
        "Red Blood Cell Count": ("red blood cell count", "rbc"),
        "Platelet Count": ("platelet count", "platelets"),
        "Cholesterol Total": ("cholesterol total", "total cholesterol"),
        "HDL Cholesterol": ("hdl cholesterol", "hdl"),
        "LDL Cholesterol": ("ldl cholesterol", "ldl"),
        "Triglycerides": ("triglycerides",),
        "HbA1c": ("hba1c", "a1c"),
        "Fasting Plasma Glucose": ("fasting plasma glucose", "fasting glucose", "fpg"),
        "Creatinine": ("creatinine",),
        "Blood Urea Nitrogen": ("blood urea nitrogen", "bun", "urea"),
        "eGFR": ("egfr", "estimated glomerular filtration rate"),
        "ALT": ("alt", "sgpt"),
        "AST": ("ast", "sgot"),
        "Bilirubin": ("bilirubin",),
        "TSH": ("tsh", "thyroid stimulating hormone"),
        "Troponin": ("troponin",),
    }

    VITAL_PATTERNS = {
        "Blood Pressure": r"\b(?:blood pressure|bp)\s*[:\-]?\s*(\d{2,3})\s*/\s*(\d{2,3})\s*(mmhg)?\b",
        "Heart Rate": r"\b(?:heart rate|pulse|hr)\s*[:\-]?\s*(\d{2,3})\s*(bpm|beats/min)?\b",
        "Respiratory Rate": r"\b(?:respiratory rate|rr)\s*[:\-]?\s*(\d{1,2})\s*(/min|breaths/min)?\b",
        "Temperature": r"\b(?:temperature|temp)\s*[:\-]?\s*(\d{2,3}(?:\.\d)?)\s*(c|f|°c|°f)?\b",
        "Oxygen Saturation": r"\b(?:spo2|oxygen saturation|o2 sat)\s*[:\-]?\s*(\d{2,3})\s*(%)?\b",
    }

    LAB_LINE_RE = re.compile(
        r"(?P<name>[A-Za-z][A-Za-z0-9 /\-\(\)]{1,60}?)\s*[:=\-]\s*"
        r"(?P<value>[<>]?\s*\d+(?:\.\d+)?)\s*"
        r"(?P<unit>mg/dL|g/dL|%|uIU/mL|mIU/L|x10\^3/uL|x10\^6/uL|mmol/L|mL/min/1\.73m2|U/L|ng/mL|bpm|mmHg)?"
        r"(?:\s*\((?P<status>[^)]{1,80})\))?",
        re.IGNORECASE,
    )

    RANGE_RE = re.compile(
        r"(?:ref(?:erence)?(?: range)?|normal)\s*[:=\-]?\s*"
        r"(?P<range>[<>]?\s*\d+(?:\.\d+)?\s*(?:-|to)\s*[<>]?\s*\d+(?:\.\d+)?)",
        re.IGNORECASE,
    )

    def classify_report(self, text: str) -> str:
        lower = text.lower()
        scores = {
            report_type: sum(1 for hint in hints if hint in lower)
            for report_type, hints in self.REPORT_HINTS.items()
        }
        report_type, score = max(scores.items(), key=lambda item: item[1])
        return report_type if score > 0 else "general_medical_report"

    def parse(self, text: str) -> dict:
        findings = self.extract_lab_findings(text)
        findings.extend(self.extract_vitals(text))
        entities = self.extract_named_entities(text)
        report_type = self.classify_report(text)
        return {
            "report_type": report_type,
            "findings": findings,
            "entities": entities,
        }

    def extract_lab_findings(self, text: str) -> list[MedicalFinding]:
        findings = []
        seen = set()
        for match in self.LAB_LINE_RE.finditer(text):
            raw_name = self._clean_name(match.group("name"))
            canonical_name = self._canonical_lab_name(raw_name)
            if not canonical_name:
                continue
            value = match.group("value").replace(" ", "")
            unit = match.group("unit")
            if self._is_vital_label(canonical_name, value, unit):
                continue
            status = self._normalize_status(match.group("status") or self._infer_status(canonical_name, value))
            reference_range = self._nearby_reference_range(text, match.end())
            key = (canonical_name.lower(), value, unit)
            if key in seen:
                continue
            seen.add(key)
            findings.append(
                MedicalFinding(
                    name=canonical_name,
                    value=value,
                    unit=unit,
                    category="lab_test",
                    reference_range=reference_range,
                    status=status,
                    description=f"Extracted {canonical_name} value of {value} {unit or ''}.",
                )
            )
        return findings

    def extract_vitals(self, text: str) -> list[MedicalFinding]:
        findings = []
        for name, pattern in self.VITAL_PATTERNS.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                if name == "Blood Pressure":
                    value = f"{match.group(1)}/{match.group(2)}"
                    unit = "mmHg"
                else:
                    value = match.group(1)
                    unit = match.group(2) or self._default_vital_unit(name)
                findings.append(
                    MedicalFinding(
                        name=name,
                        value=value,
                        unit=unit,
                        category="vital_sign",
                        status=self._infer_status(name, value),
                        description=f"Extracted vital sign {name}: {value} {unit or ''}.",
                    )
                )
        return findings

    def extract_named_entities(self, text: str) -> dict[str, list[dict]]:
        lower = text.lower()
        grouped = {"diseases": [], "symptoms": [], "medications": []}
        seen = set()
        for pattern in self.ENTITY_PATTERNS:
            if any(re.search(rf"\b{re.escape(alias)}\b", lower) for alias in pattern.aliases):
                key = (pattern.category, pattern.name)
                if key in seen:
                    continue
                seen.add(key)
                bucket = f"{pattern.category}s" if pattern.category != "medication" else "medications"
                grouped[bucket].append({"name": pattern.name, "category": pattern.category})
        return grouped

    def _canonical_lab_name(self, raw_name: str) -> str | None:
        normalized = raw_name.lower()
        noisy_names = {"patient", "patient name", "test", "notes", "comments", "clinical assessment"}
        if normalized in noisy_names:
            return None
        for canonical, aliases in self.LAB_PATTERNS.items():
            if any(alias in normalized or normalized in alias for alias in aliases):
                return canonical
        return raw_name if any(char.isdigit() for char in raw_name) is False and len(raw_name) <= 40 else None

    def _clean_name(self, name: str) -> str:
        name = re.sub(r"[\r\n]+", " ", name)
        name = re.sub(r"\s+", " ", name)
        return name.strip(" :-")

    def _is_vital_label(self, name: str, value: str, unit: str | None) -> bool:
        lower = name.lower()
        if lower in {"blood pressure", "heart rate", "respiratory rate", "temperature", "oxygen saturation"}:
            return True
        if "/" in value and "blood pressure" in lower:
            return True
        if unit and unit.lower() in {"bpm", "mmhg", "%"} and lower in {"heart rate", "blood pressure", "oxygen saturation"}:
            return True
        return False

    def _nearby_reference_range(self, text: str, start: int) -> str | None:
        window = text[start:start + 120]
        match = self.RANGE_RE.search(window)
        return match.group("range") if match else None

    def _normalize_status(self, status: str | None) -> str:
        if not status:
            return "normal"
        lower = status.lower()
        if "critical" in lower:
            return "critical"
        if any(word in lower for word in ("high", "elevated", "abnormal")):
            return "elevated"
        if "low" in lower:
            return "low"
        if "normal" in lower:
            return "normal"
        return lower.strip()

    def _infer_status(self, name: str, value: str) -> str:
        numeric = self._number(value)
        if numeric is None:
            return "normal"
        key = name.lower()
        if "hba1c" in key:
            return "critical" if numeric >= 8.5 else ("elevated" if numeric >= 5.7 else "normal")
        if "glucose" in key:
            return "elevated" if numeric >= 126 else "normal"
        if "ldl" in key:
            return "elevated" if numeric >= 130 else "normal"
        if "cholesterol" in key:
            return "elevated" if numeric >= 200 else "normal"
        if "triglycerides" in key:
            return "elevated" if numeric >= 150 else "normal"
        if "white blood" in key or key == "wbc":
            return "elevated" if numeric > 11 else ("low" if numeric < 4 else "normal")
        if "hemoglobin" in key:
            return "low" if numeric < 12 else "normal"
        if "creatinine" in key:
            return "elevated" if numeric > 1.3 else "normal"
        if "egfr" in key:
            return "low" if numeric < 60 else "normal"
        if "alt" in key or "ast" in key:
            return "elevated" if numeric > 40 else "normal"
        if "blood pressure" in key and "/" in value:
            systolic, diastolic = value.split("/", 1)
            return "elevated" if int(systolic) >= 130 or int(diastolic) >= 80 else "normal"
        if "heart rate" in key:
            return "elevated" if numeric > 100 else ("low" if numeric < 60 else "normal")
        if "oxygen" in key:
            return "low" if numeric < 94 else "normal"
        if "temperature" in key:
            return "elevated" if numeric >= 100.4 or numeric >= 38 else "normal"
        return "normal"

    def _default_vital_unit(self, name: str) -> str | None:
        return {
            "Heart Rate": "bpm",
            "Respiratory Rate": "breaths/min",
            "Temperature": "F",
            "Oxygen Saturation": "%",
        }.get(name)

    def _number(self, value: str) -> float | None:
        match = re.search(r"\d+(?:\.\d+)?", value)
        return float(match.group(0)) if match else None
