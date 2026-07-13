from typing import List
from src.extraction.schema import MedicalFinding

class MedicalNormalizer:
    def __init__(self):
        # High fidelity mappings dictionary representing standardized clinical dictionaries
        self.loinc_db = {
            "complete blood count": "24323-8",
            "cholesterol total": "2093-3",
            "hdl cholesterol": "2085-9",
            "ldl cholesterol": "13457-7",
            "triglycerides": "2571-8",
            "hba1c": "4548-4",
            "fasting plasma glucose": "1558-6",
            "oral glucose tolerance": "1563-6",
            "white blood cell count": "6690-2",
            "red blood cell count": "789-8",
            "hemoglobin": "718-7",
            "platelet count": "777-3",
            "tsh": "11579-0",
            "blood pressure": "85354-9",
            "heart rate": "8867-4",
            "creatinine": "2160-0",
            "blood urea nitrogen": "3094-0",
            "urea": "3094-0",
            "egfr": "33914-3",
            "alt": "1742-6",
            "ast": "1920-8",
            "bilirubin": "1975-2",
            "troponin": "89579-7",
            "respiratory rate": "9279-1",
            "temperature": "8310-5",
            "oxygen saturation": "59408-5",
            "ecg": "11526-1",
            "electrocardiogram": "11526-1",
            "x-ray": "59884-1",
            "mri": "38208-5",
            "ct scan": "24729-0"
        }

        self.snomed_db = {
            "complete blood count": "103693007",
            "cholesterol total": "121868005",
            "hdl cholesterol": "28114008",
            "ldl cholesterol": "113079009",
            "triglycerides": "14682006",
            "hba1c": "43396009",
            "fasting plasma glucose": "250392003",
            "white blood cell count": "113028004",
            "red blood cell count": "14089001",
            "hemoglobin": "34994002",
            "platelet count": "60233008",
            "tsh": "37111003",
            "blood pressure": "75367002",
            "heart rate": "364075005",
            "respiratory rate": "86290005",
            "temperature": "386725007",
            "oxygen saturation": "103228002",
            "creatinine": "70901006",
            "blood urea nitrogen": "365755003",
            "egfr": "80274001",
            "alt": "34608000",
            "ast": "34608000",
            "bilirubin": "365636006",
            "troponin": "10265007",
            "ecg": "163141003",
            "electrocardiogram": "163141003",
            "x-ray": "299073007",
            "mri": "309629006",
            "ct scan": "363679005",
            "fever": "386661002",
            "sore throat": "162332007",
            "chest tightness": "271813007",
            "polydipsia": "17173007",
            "polyuria": "56574000",
            "diabetes mellitus": "73211009",
            "hypertension": "38341003",
            "chronic kidney disease": "709044004",
            "asthma": "195967001",
            "myocardial infarction": "22298006",
            "cough": "49727002",
            "shortness of breath": "267036007",
            "metformin": "372567009",
            "atorvastatin": "387458008",
            "aspirin": "387458008",
            "paracetamol": "387517004",
            "ibuprofen": "387207008",
            "lisinopril": "386872004",
            "albuterol": "372897005"
        }

        self.icd10_db = {
            "complete blood count": "R70.0",
            "cholesterol total": "E78.00",
            "hdl cholesterol": "E78.6",
            "ldl cholesterol": "E78.01",
            "triglycerides": "E78.1",
            "hba1c": "E11.9",
            "fasting plasma glucose": "R73.09",
            "white blood cell count": "D72.829",
            "red blood cell count": "D72.8",
            "hemoglobin": "D50.9",
            "platelet count": "D69.6",
            "tsh": "E03.9",
            "blood pressure": "I10",
            "heart rate": "R00.9",
            "respiratory rate": "R06.9",
            "temperature": "R50.9",
            "oxygen saturation": "R09.02",
            "creatinine": "R94.4",
            "blood urea nitrogen": "R94.4",
            "egfr": "R94.4",
            "alt": "R94.5",
            "ast": "R94.5",
            "bilirubin": "R17",
            "troponin": "R79.89",
            "ecg": "R94.31",
            "electrocardiogram": "R94.31",
            "fever": "R50.9",
            "sore throat": "J02.9",
            "chest tightness": "R07.89",
            "polydipsia": "R63.1",
            "polyuria": "R35.0",
            "diabetes mellitus": "E11.9",
            "hypertension": "I10",
            "chronic kidney disease": "N18.9",
            "asthma": "J45.909",
            "myocardial infarction": "I21.9",
            "cough": "R05.9",
            "shortness of breath": "R06.02"
        }

    def normalize(self, findings: List[MedicalFinding]) -> List[MedicalFinding]:
        """
        Enriches clinical entities with matching LOINC, SNOMED, and ICD-10 medical codes.
        """
        normalized_list = []
        for f in findings:
            name_lower = f.name.lower().strip()
            
            loinc = self._match_code(self.loinc_db, name_lower)
            snomed = self._match_code(self.snomed_db, name_lower)
            icd10 = self._match_code(self.icd10_db, name_lower)
            
            # Enrich the finding
            f.loinc_code = loinc or f.loinc_code or "N/A"
            f.snomed_code = snomed or f.snomed_code or "N/A"
            f.icd10_code = icd10 or f.icd10_code or "N/A"
            
            # Contextual patient descriptions
            f.description = self._generate_description(f)
            
            normalized_list.append(f)
            
        return normalized_list

    def _generate_description(self, f: MedicalFinding) -> str:
        name_lower = f.name.lower()
        if "cholesterol" in name_lower or "ldl" in name_lower or "triglycerides" in name_lower:
            if f.status in ["high", "abnormal", "elevated"]:
                return f"High levels of lipids in your blood increase risk for heart disease. Discuss dietary adjustments and physical activity with your clinician."
            return "Lipid levels are within optimal range, contributing to good cardiovascular health."
        elif "hba1c" in name_lower or "glucose" in name_lower:
            if f.status in ["high", "critical high", "abnormal", "elevated"]:
                return f"Elevated blood glucose indicators indicate risk for Pre-diabetes or Type 2 Diabetes mellitus. Requires immediate clinical dietary evaluation."
            return "Glucose markers are within normal biological values."
        elif "wbc" in name_lower or "white blood cell" in name_lower:
            if f.status in ["high", "abnormal", "elevated"]:
                return f"Elevated White Blood Cells typically point to active physiological responses like systemic inflammation, infection, or stress."
            return "White Blood Count checks out healthy."
        elif "blood pressure" in name_lower:
            return "High systemic blood pressure readings suggest hypertension risks which strain the arteries."
        else:
            return f"Measured biological value: {f.value or ''} {f.unit or ''}. Status flag: {f.status}."

    def _match_code(self, db: dict[str, str], name_lower: str) -> str | None:
        for key, code in db.items():
            if key in name_lower or name_lower in key:
                return code
        return None
