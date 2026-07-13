import re
from typing import Dict, List

from src.extraction.schema import MedicalFinding, MedicalGuideline


class MedicalAnalysisGenerator:
    def analyze(self, findings: List[MedicalFinding], guidelines: List[MedicalGuideline]) -> Dict[str, object]:
        abnormal_findings = [f.name for f in findings if f.status.lower() not in ["normal", "optimal"]]
        possible_conditions = self._infer_conditions(findings, guidelines)
        red_flags = self._detect_red_flags(findings)
        urgency = self._classify_urgency(findings, red_flags)
        risk_analysis = self._assess_risk(findings, red_flags)
        specialists = self._recommend_specialists(findings, guidelines, red_flags)
        follow_up = self._build_follow_up(abnormal_findings, possible_conditions)
        lifestyle = self._build_lifestyle(abnormal_findings)
        source_attribution = self._collect_sources(guidelines)

        clinical_summary = self.generate_clinical_summary(
            findings, abnormal_findings, possible_conditions, urgency, risk_analysis, red_flags, specialists
        )
        patient_explanation = self.generate_patient_explanation(findings, abnormal_findings)

        return {
            "clinical_summary": clinical_summary,
            "patient_explanation": patient_explanation,
            "abnormal_findings": abnormal_findings,
            "possible_conditions": possible_conditions,
            "follow_up_recommendations": follow_up,
            "lifestyle_recommendations": lifestyle,
            "risk_analysis": risk_analysis,
            "urgency_classification": urgency,
            "red_flags": red_flags,
            "recommended_specialists": specialists,
            "source_attribution": source_attribution,
        }

    def _infer_conditions(self, findings: List[MedicalFinding], guidelines: List[MedicalGuideline]) -> List[str]:
        conditions = set()
        for finding in findings:
            key = finding.name.lower()
            if "hba1c" in key or "glucose" in key or "diabetes" in key:
                conditions.add("Type 2 diabetes mellitus")
            if "blood pressure" in key or "hypertension" in key:
                conditions.add("Hypertension")
            if "cholesterol" in key or "ldl" in key or "triglyceride" in key:
                conditions.add("Dyslipidemia")
            if "wbc" in key or "white blood cell" in key:
                conditions.add("Potential infection or inflammation")
            if "creatinine" in key or "bun" in key or "eGFR" in key:
                conditions.add("Renal impairment")
            if "fever" in key or "temperature" in key:
                conditions.add("Febrile illness")
        for guideline in guidelines:
            title = guideline.guideline_name.lower()
            if "diabetes" in title:
                conditions.add("Diabetes mellitus")
            if "cardiovascular" in title or "hypertension" in title:
                conditions.add("Cardiovascular risk")
        return sorted(conditions)

    def _detect_red_flags(self, findings: List[MedicalFinding]) -> List[str]:
        flags = []
        for finding in findings:
            name = finding.name.lower()
            status = finding.status.lower()
            if any(term in name for term in ["chest pain", "angina", "shortness of breath", "dyspnea"]):
                flags.append("Cardiorespiratory distress")
            if any(term in name for term in ["confusion", "altered mental status", "fainting"]):
                flags.append("Neurological impairment")
            if any(term in name for term in ["temperature", "fever"]) and finding.value:
                try:
                    temp = float(re.sub(r"[^0-9.]", "", finding.value))
                    if temp >= 103:
                        flags.append("High fever")
                except Exception:
                    pass
            if any(term in name for term in ["wbc", "leukocyte"]) and finding.value:
                try:
                    val = float(re.sub(r"[^0-9.]", "", finding.value))
                    if val > 11.0:
                        flags.append("Leukocytosis")
                except Exception:
                    pass
            if "a1c" in name and finding.value:
                try:
                    val = float(re.sub(r"[^0-9.]", "", finding.value))
                    if val >= 8.0:
                        flags.append("Poor glycemic control")
                except Exception:
                    pass
        return sorted(set(flags))

    def _classify_urgency(self, findings: List[MedicalFinding], red_flags: List[str]) -> str:
        if red_flags:
            return "Emergency" if any("Cardiorespiratory" in flag for flag in red_flags) else "Urgent"
        if any(f.status.lower() in ["critical", "severe"] for f in findings):
            return "Urgent"
        return "Routine"

    def _assess_risk(self, findings: List[MedicalFinding], red_flags: List[str]) -> str:
        if any("Cardiorespiratory" in flag for flag in red_flags) or any(f.status.lower() == "critical" for f in findings):
            return "High risk"
        if red_flags or any(f.status.lower() in ["elevated", "abnormal", "moderate"] for f in findings):
            return "Moderate risk"
        return "Low risk"

    def _recommend_specialists(
        self,
        findings: List[MedicalFinding],
        guidelines: List[MedicalGuideline],
        red_flags: List[str],
    ) -> List[str]:
        specialists = set()
        text = " ".join([f.name.lower() for f in findings])
        if any(keyword in text for keyword in ["heart", "hypertension", "cholesterol", "ldl", "angina"]):
            specialists.add("Cardiologist")
        if any(keyword in text for keyword in ["diabetes", "hba1c", "glucose", "insulin"]):
            specialists.add("Endocrinologist")
        if any(keyword in text for keyword in ["creatinine", "bun", "egfr", "renal", "kidney"]):
            specialists.add("Nephrologist")
        if any(keyword in text for keyword in ["breath", "asthma", "pneumonia", "cough"]):
            specialists.add("Pulmonologist")
        if any(keyword in text for keyword in ["fever", "infection", "wbc"]):
            specialists.add("Infectious disease specialist")
        if red_flags:
            specialists.add("Emergency care")
        if not specialists:
            specialists.add("General physician")
        return sorted(specialists)

    def _build_follow_up(self, abnormal_findings: List[str], possible_conditions: List[str]) -> List[str]:
        recommendations = []
        if abnormal_findings:
            recommendations.append(
                "Review abnormal findings with a clinician and consider targeted follow-up testing."
            )
        if possible_conditions:
            recommendations.append(
                "Discuss the likely conditions with your healthcare provider to confirm diagnosis and treatment."
            )
        recommendations.append(
            "Schedule periodic lab monitoring and share these results with your primary care provider."
        )
        return recommendations

    def _build_lifestyle(self, abnormal_findings: List[str]) -> List[str]:
        suggestions = []
        if any("cholesterol" in f.lower() or "triglyceride" in f.lower() for f in abnormal_findings):
            suggestions.append("Adopt a heart-healthy diet low in saturated fat and refined carbs.")
        if any("a1c" in f.lower() or "glucose" in f.lower() for f in abnormal_findings):
            suggestions.append("Increase physical activity and reduce simple sugars to help manage blood glucose.")
        if not suggestions:
            suggestions.append("Maintain regular exercise, balanced nutrition, and adequate sleep.")
        return suggestions

    def _collect_sources(self, guidelines: List[MedicalGuideline]) -> List[str]:
        sources = []
        for guideline in guidelines:
            if guideline.source_name and guideline.guideline_name:
                sources.append(f"{guideline.source_name}: {guideline.guideline_name}")
        return sources

    def generate_clinical_summary(
        self,
        findings: List[MedicalFinding],
        abnormal_findings: List[str],
        possible_conditions: List[str],
        urgency: str,
        risk_analysis: str,
        red_flags: List[str],
        specialists: List[str],
    ) -> str:
        lines = [
            "CLINICAL REPORT SUMMARY",
            "-----------------------",
            f"Urgency: {urgency}",
            f"Risk Analysis: {risk_analysis}",
        ]
        if red_flags:
            lines.append("Red Flags Detected:")
            for flag in red_flags:
                lines.append(f" - {flag}")
        if abnormal_findings:
            lines.append("Abnormal Findings:")
            for finding in abnormal_findings:
                lines.append(f" - {finding}")
        if possible_conditions:
            lines.append("Possible Conditions:")
            for condition in possible_conditions:
                lines.append(f" - {condition}")
        if specialists:
            lines.append("Recommended Specialists:")
            lines.append(f" - {', '.join(specialists)}")
        return "\n".join(lines)

    def generate_patient_explanation(self, findings: List[MedicalFinding], abnormal_findings: List[str]) -> str:
        if not findings:
            return "No significant clinical findings were extracted from your report. Continue with routine preventive care."

        lines = [
            "PATIENT-FRIENDLY SUMMARY",
            "-------------------------",
            "Here is what we found in simpler language:",
        ]
        for finding in findings:
            label = finding.name
            status = finding.status.capitalize()
            value = finding.value or "N/A"
            unit = f" {finding.unit}" if finding.unit else ""
            lines.append(f"• {label}: {value}{unit} — {status}.")
            if finding.description:
                lines.append(f"  {finding.description}")

        if abnormal_findings:
            lines.append("\nNext steps:")
            lines.append(" - Talk to your doctor about these abnormal results.")
            lines.append(" - Share this report and ask about treatment or monitoring plans.")
        else:
            lines.append("\nThese results are within expected ranges. Keep up regular check-ups and healthy habits.")

        return "\n".join(lines)
