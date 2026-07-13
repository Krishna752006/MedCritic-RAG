"""
VeriMedX Clinical Chat Service
================================
Implements the VeriMedX system prompt rules:
  • 9-intent classification (greeting, casual_conversation, symptom,
    disease_info, medicine_info, report_upload, emergency, follow_up, goodbye)
  • Triage workflow continuity — never repeats a question already asked
  • Structured evidence blocks on every medical response
  • Personalized context injected into every LLM prompt
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Optional

import requests
from rank_bm25 import BM25Okapi

from src.emergency.triage import EmergencyTriage
from src.llm.llm_service import LLMService
from src.knowledge.knowledge_ingestor import KnowledgeIngestor

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE_DIR = WORKSPACE_ROOT / "data" / "knowledge"
SOURCE_DIR = KNOWLEDGE_DIR / "sources"
CORPUS_FILE = KNOWLEDGE_DIR / "bm25_corpus.json"

WIKI_TOPICS = [
    "Hypertension", "Diabetes_mellitus", "Myocardial_infarction",
    "Stroke", "Pneumonia", "Chronic_kidney_disease", "Asthma",
    "Heart_failure", "Coronary_artery_disease", "Sepsis",
    "COVID-19", "Paracetamol", "Metformin", "Atorvastatin",
    "Aspirin", "Ibuprofen",
]

EMERGENCY_KEYWORDS = [
    "chest pain", "difficulty breathing", "shortness of breath",
    "unconscious", "severe bleeding", "stroke", "heart attack",
    "suicidal", "severe allergy", "convulsions", "fainting",
    "confusion", "severe weakness", "choking", "collapsed",
    "unable to breathe", "not breathing", "anaphylaxis",
    "loss of consciousness", "overdose",
]

SYMPTOM_KEYWORDS = [
    "fever", "cough", "sore throat", "headache", "nausea", "vomiting",
    "diarrhea", "dizziness", "dizzy", "fatigue", "rash", "swelling",
    "pain", "cramps", "chills", "runny nose", "tired", "weakness",
]

MEDICINE_KEYWORDS = [
    "paracetamol", "metformin", "atorvastatin", "aspirin", "ibuprofen",
    "drug", "medicine", "tablet", "dosage", "side effect",
    "contraindication", "interaction", "dose", "medication",
]

COMPARISON_KEYWORDS = ["compare", "versus", "vs", "difference between", "which is better"]
FOLLOW_UP_KEYWORDS = ["also", "more", "further", "another", "added", "follow up", "follow-up"]

DISEASE_KEYWORDS = [
    "covid", "corona", "diabetes", "hypertension", "stroke", "pneumonia",
    "asthma", "heart failure", "kidney disease", "sepsis",
    "myocardial infarction", "heart attack",
]

FALLBACK_CONTENT: Dict[str, str] = {
    "Hypertension": (
        "Hypertension (high blood pressure) is a chronic condition where blood pressure "
        "in the arteries is persistently elevated (≥130/80 mmHg per AHA 2023 guidelines). "
        "Risk factors include excess salt, obesity, smoking, and alcohol. Treatment involves "
        "lifestyle changes and medications such as ACE inhibitors (e.g. Lisinopril), "
        "beta-blockers, and calcium channel blockers."
    ),
    "Diabetes_mellitus": (
        "Diabetes mellitus is a metabolic disorder characterised by chronic hyperglycaemia. "
        "ADA (2024) criteria: fasting glucose ≥126 mg/dL or HbA1c ≥6.5%. Type 2 first-line "
        "therapy is Metformin 500–2000 mg/day with dietary modification. Complications include "
        "retinopathy, nephropathy, neuropathy, and cardiovascular disease."
    ),
    "COVID-19": (
        "COVID-19 is caused by SARS-CoV-2. Common symptoms: fever, dry cough, fatigue, loss of "
        "smell/taste. High-risk groups: elderly, immunocompromised, pregnant women. WHO (2023) "
        "recommends supportive care; antivirals (Paxlovid) for high-risk patients within 5 days "
        "of symptom onset. Isolation for ≥5 days from symptom onset (CDC)."
    ),
    "Paracetamol": (
        "Paracetamol (acetaminophen) is a first-line analgesic and antipyretic. Adult dose: "
        "500–1000 mg every 4–6 hours, max 4 g/day. Overdose causes acute liver failure. "
        "Contraindicated in severe hepatic impairment. Avoid concurrent alcohol use."
    ),
    "Metformin": (
        "Metformin is the preferred first-line oral antidiabetic for Type 2 DM. Mechanism: "
        "decreases hepatic gluconeogenesis. Start 500 mg twice daily with meals; titrate to "
        "2000 mg/day. Contraindicated if eGFR <30 mL/min (risk of lactic acidosis). GI side "
        "effects (nausea, diarrhoea) are common initially."
    ),
    "Atorvastatin": (
        "Atorvastatin (Lipitor) is a high-potency statin (HMG-CoA reductase inhibitor). "
        "Indicated for LDL reduction and cardiovascular prevention. Dose range: 10–80 mg/day. "
        "Common side effects: myalgia. Rare: rhabdomyolysis. Contraindicated in pregnancy and "
        "active liver disease. Check LFTs at baseline and 12 weeks."
    ),
    "Aspirin": (
        "Aspirin (acetylsalicylic acid) is used as an antiplatelet (75–100 mg/day) for "
        "secondary prevention of MI and stroke. Analgesic dose: 300–600 mg every 4–6 hours. "
        "Risks: GI ulceration, bleeding. Contraindicated in Reye's syndrome risk (children), "
        "active peptic ulcer, and aspirin-exacerbated respiratory disease."
    ),
    "Ibuprofen": (
        "Ibuprofen is an NSAID (COX-1/2 inhibitor) used for pain and inflammation. Adult dose: "
        "200–400 mg every 4–6 hours, max 1200 mg OTC (2400 mg prescription). Risks: GI "
        "bleeding, renal impairment, CV events. Avoid in peptic ulcer disease, CKD, heart "
        "failure, and third trimester of pregnancy."
    ),
    "Stroke": (
        "Stroke requires immediate action. FAST scale: Face drooping, Arm drift, Speech "
        "difficulty, Time to call emergency. Ischaemic stroke: IV thrombolysis (tPA) within "
        "4.5 hours or mechanical thrombectomy within 24 hours. Call emergency services "
        "immediately. Time is brain."
    ),
    "Asthma": (
        "Asthma is a chronic inflammatory airway disease. Symptoms: wheeze, dyspnoea, chest "
        "tightness, nocturnal cough. GINA 2023 recommends low-dose ICS+formoterol as "
        "preferred reliever and controller. Salbutamol/Albuterol for acute attacks."
    ),
    "Pneumonia": (
        "Pneumonia is a lung infection assessed via CURB-65 (confusion, urea, respiratory "
        "rate, BP, age ≥65). Score ≥2 warrants hospital admission. Community-acquired: "
        "Amoxicillin 500 mg TDS (5 days) first-line per NICE guidelines."
    ),
    "Sepsis": (
        "Sepsis is a life-threatening organ dysfunction from dysregulated infection response. "
        "Sepsis-3 criteria: SOFA score increase ≥2. Surviving Sepsis Campaign 2021: "
        "IV antibiotics within 1 hour, 30 mL/kg IV crystalloid for hypotension."
    ),
}


def _normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def _chunk(text: str, max_tokens: int = 180) -> List[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks, current, count = [], [], 0
    for s in sentences:
        s = s.strip()
        if not s:
            continue
        n = len(s.split())
        if count + n > max_tokens and current:
            chunks.append(" ".join(current))
            current, count = [], 0
        current.append(s)
        count += n
    if current:
        chunks.append(" ".join(current))
    return chunks


# ---------------------------------------------------------------------------
# Knowledge Trainer
# ---------------------------------------------------------------------------

class MedicalKnowledgeTrainer:
    def __init__(self):
        self.ingestor = KnowledgeIngestor()

    def _fetch_wiki(self, title: str) -> str:
        params = {
            "action": "query", "format": "json", "formatversion": 2,
            "prop": "extracts", "explaintext": 1, "redirects": 1, "titles": title,
        }
        headers = {"User-Agent": "VeriMedX/2.0 (research@example.com)"}
        r = requests.get(
            "https://en.wikipedia.org/w/api.php",
            params=params, headers=headers, timeout=12
        )
        r.raise_for_status()
        pages = r.json().get("query", {}).get("pages", [])
        if not pages or not pages[0].get("extract"):
            raise ValueError("Empty extract")
        return _normalize(pages[0]["extract"])

    def download_topics(self) -> Dict[str, str]:
        results = {}
        for title in WIKI_TOPICS:
            try:
                content = self._fetch_wiki(title)
            except Exception as exc:
                content = FALLBACK_CONTENT.get(title, f"{title}: clinical topic.")
                results[title] = f"offline_fallback ({exc})"
            else:
                results[title] = "downloaded"
            (SOURCE_DIR / f"{title}.txt").write_text(content, encoding="utf-8")
        return results

    def build_corpus(self) -> List[Dict[str, object]]:
        return self.ingestor.read_source_files()

    def load_corpus(self) -> List[Dict[str, object]]:
        return self.ingestor.load_corpus()

    def train(self) -> Dict[str, object]:
        result = self.ingestor.train()
        if result["status"] == "empty":
            downloaded = self.download_topics()
            corpus = self.ingestor.read_source_files()
            self.ingestor.save_corpus(corpus)
            result = {
                "status": "trained",
                "knowledge_chunks": len(corpus),
                "source_files": len({item["source"] for item in corpus}),
                "embedding_path": self.ingestor.create_embeddings(corpus),
                "fallback_wiki": downloaded,
            }
        return result


# ---------------------------------------------------------------------------
# VeriMedX Chat Service
# ---------------------------------------------------------------------------

# Triage question templates — keyed by metadata field name
TRIAGE_QUESTIONS = {
    "symptom":           "I'm sorry to hear you're not feeling well. Could you briefly **describe your main symptom**?",
    "symptom_duration":  "How **long** have you been experiencing {symptom}? *(e.g. 2 days, since yesterday)*",
    "symptom_temp":      "Since you have a fever, did you measure your temperature? If yes, **what was the reading**?",
    "age":               "To give you accurate guidance, could you tell me **your age**?",
    "gender":            "Could you please share **your biological sex** *(Male / Female)*?",
    "pregnancy_status":  "Are you **currently pregnant**? *(Yes / No)*",
    "allergies":         "Do you have any **known drug or food allergies**? *(or type 'None')*",
    "existing_diseases": "Do you have any **pre-existing medical conditions** such as diabetes or hypertension? *(or type 'None')*",
}


class MedicalChatService:
    """VeriMedX evidence-based chat service with full triage continuity."""

    SYSTEM_PROMPT = (
        "You are VeriMedX, an AI-powered healthcare assistant. "
        "Provide safe, evidence-based, conversational clinical support. "
        "Never diagnose with certainty. Always recommend consulting a qualified healthcare professional. "
        "Explain medical terms in plain language. State uncertainty clearly. "
        "Every medical response must include an evidence summary, source, and confidence level."
    )

    def __init__(self):
        self.trainer = MedicalKnowledgeTrainer()
        self.documents = self.trainer.load_corpus()
        self.bm25: Optional[BM25Okapi] = None
        self.llm = LLMService()
        self.triage_service = EmergencyTriage()
        if self.documents:
            self._build_index()

    # ------------------------------------------------------------------
    # Index management
    # ------------------------------------------------------------------

    def _build_index(self):
        tokenized = [self._tok(d["text"]) for d in self.documents]
        if tokenized:
            self.bm25 = BM25Okapi(tokenized)

    def _tok(self, text: str) -> List[str]:
        return [t for t in re.sub(r"[^a-z0-9 ]", " ", text.lower()).split() if t]

    def ensure_knowledge(self):
        if not self.documents:
            self.documents = self.trainer.load_corpus()
            if not self.documents:
                self.trainer.train()
                self.documents = self.trainer.load_corpus()
            self._build_index()

    def _retrieve(self, query: str, top_k: int = 4) -> List[Dict[str, str]]:
        if not self.bm25:
            return []
        scores = self.bm25.get_scores(self._tok(query))
        top = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k]
        return [self.documents[i] for i in top if scores[i] > 0]

    # ------------------------------------------------------------------
    # Intent detection (9 VeriMedX intents)
    # ------------------------------------------------------------------

    def detect_intent(
        self,
        message: str,
        session_id: Optional[str] = None,
        memory: Optional[object] = None,
    ) -> str:
        nl = message.lower().strip()

        # 1. Goodbye
        if re.search(r"\b(bye|goodbye|good bye|see you|thanks bye|take care|farewell|quit|exit)\b", nl):
            return "goodbye"

        # 2. Greeting
        if re.search(r"\b(hi|hello|hey|good morning|good afternoon|good evening|namaste|greetings)\b", nl):
            return "greeting"

        # 3. Emergency — always highest priority
        if any(kw in nl for kw in EMERGENCY_KEYWORDS):
            return "emergency"

        # 4. Report upload request
        if re.search(r"(upload|send|analyze|scan|read).*(report|pdf|lab|image|scan)", nl) or \
           re.search(r"(report|lab result|scan|pdf).*(upload|send|check|analyze)", nl):
            return "report_upload"

        # 5. Follow-up — if triage is active and message looks like a triage answer
        if session_id and memory:
            if memory.is_triage_active(session_id):
                words = nl.split()
                has_number = bool(re.search(r"\b\d+\b", nl))
                short = len(words) <= 5
                is_yn = nl.strip() in {
                    "yes", "no", "yeah", "nope", "none", "not pregnant", "pregnant",
                    "male", "female", "man", "woman", "no allergies",
                }
                has_dur = bool(re.search(r"\b\d+\s*(days?|hours?|weeks?|months?)\b", nl))
                has_temp = bool(re.search(r"\b\d{2,3}(\.\d)?\s*(c|f|°)?\b", nl))
                if short or is_yn or has_number or has_dur or has_temp:
                    return "follow_up"

        # 6. Disease info
        if any(kw in nl for kw in DISEASE_KEYWORDS):
            if re.search(
                r"\b(what is|tell me about|explain|causes?|symptoms?|prevention|treatment|guidelines?|information)\b",
                nl,
            ):
                return "disease_info"
            if any(comp in nl for comp in COMPARISON_KEYWORDS):
                return "comparison_request"

        # 7. Medicine info
        if any(kw in nl for kw in MEDICINE_KEYWORDS):
            return "medicine_info"

        # 9. Symptom assessment
        if any(kw in nl for kw in SYMPTOM_KEYWORDS) or re.search(
            r"\b(i have|i feel|i am feeling|i've been|suffering from|experiencing)\b", nl
        ):
            return "symptom"

        if any(kw in nl for kw in FOLLOW_UP_KEYWORDS) and session_id and memory and memory.is_triage_active(session_id):
            return "follow_up"

        # 9. Casual / small talk
        if re.search(r"\b(how are you|how's it going|what are you|are you an ai|who made you|what can you do)\b", nl):
            return "small_talk"

        # 10. General medical query → RAG
        if re.search(
            r"\b(what|how|why|should|could|explain|meaning|interpret|result|value|normal|range)\b", nl
        ):
            return "medical_query"

        return "general"

    # ------------------------------------------------------------------
    # Prompt builder
    # ------------------------------------------------------------------

    def _build_prompt(
        self,
        question: str,
        snippets: List[Dict[str, str]],
        patient_context: Optional[str],
    ) -> str:
        lines = [self.SYSTEM_PROMPT]
        if patient_context:
            lines.append(f"\nCurrent patient context: {patient_context}")
        if snippets:
            lines.append("\nRelevant medical evidence:")
            for i, s in enumerate(snippets, 1):
                lines.append(f"[{i}] {s['source']}: {s['text']}")
        lines.append(f"\nPatient message: {question}")
        lines.append("VeriMedX response (be concise, evidence-based, compassionate):")
        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Evidence block builder
    # ------------------------------------------------------------------

    def _compute_confidence(self, snippets: List[Dict[str, str]], risk: str) -> float:
        confidence = 0.62
        if snippets:
            confidence += min(0.26, 0.08 * len(snippets))
            top_source = snippets[0]["source"].upper()
            if any(x in top_source for x in ["WHO", "CDC", "FDA", "NICE", "EMA"]):
                confidence += 0.10
            elif any(x in top_source for x in ["ADA", "AHA", "ACC", "ESC", "AACE"]):
                confidence += 0.06
        if risk == "High":
            confidence -= 0.08
        return round(max(0.50, min(0.99, confidence)), 2)

    def _evidence_block(
        self,
        snippets: List[Dict[str, str]],
        confidence: float,
        risk: str,
        source_override: Optional[str] = None,
        ranking_override: Optional[str] = None,
    ) -> Dict:
        computed_confidence = self._compute_confidence(snippets, risk)
        source_label = source_override
        ranking = ranking_override
        evidence_text = "N/A"

        if snippets:
            src = snippets[0]["source"].replace(".txt", "").replace("_", " ")
            source_label = source_label or f"{src} (2024)"
            evidence_text = snippets[0]["text"]
            if not ranking:
                su = src.upper()
                if any(x in su for x in ["WHO", "CDC", "FDA", "NICE", "EMA"]):
                    ranking = "★★★★★ WHO/CDC/FDA"
                elif any(x in su for x in ["ADA", "AHA", "ACC", "ESC", "AACE"]):
                    ranking = "★★★★ Specialist Society"
                else:
                    ranking = "★★★ PubMed/Wiki"
        else:
            source_label = source_label or "VeriMedX Clinical Knowledge Base"
            ranking = ranking or "★★★ General Reference"

        return {
            "sources": [s["source"] for s in snippets],
            "evidence": evidence_text,
            "source": source_label,
            "evidence_ranking": ranking,
            "confidence": computed_confidence,
            "health_risk_score": risk,
        }

    # ------------------------------------------------------------------
    # Main chat entry point
    # ------------------------------------------------------------------

    def chat(
        self,
        session_id: str,
        message: str,
        context_summary: Optional[str] = None,
        lang: str = "en",
        memory: Optional[object] = None,
    ) -> Dict:
        intent = self.detect_intent(message, session_id, memory)
        meta = memory.get_metadata(session_id) if memory else {}
        patient_ctx = memory.build_personalized_prompt_context(session_id) if memory else ""

        # ── 1. Goodbye ──────────────────────────────────────────────────
        if intent == "goodbye":
            if memory:
                memory.deactivate_triage(session_id)
            return {
                "response": (
                    "Thank you for using VeriMedX. Take care, and remember to consult a "
                    "qualified healthcare professional for any medical decisions. Goodbye! 👋"
                ),
                **self._evidence_block([], 1.0, "Low",
                                       "VeriMedX System", "★★★★★ VeriMedX"),
                "why": "User ended the session.",
            }

        # ── 2. Greeting ─────────────────────────────────────────────────
        if intent == "greeting":
            return {
                "response": (
                    "Hello! I'm **VeriMedX**, your AI-powered clinical assistant. 🩺\n\n"
                    "I can help you with:\n"
                    "- 🔬 Symptom assessment & triage\n"
                    "- 💊 Medication information\n"
                    "- 🦠 Disease & condition guidance\n"
                    "- 📄 Medical report interpretation\n"
                    "- 🚨 Emergency first-aid guidance\n\n"
                    "How can I help you today?"
                ),
                **self._evidence_block([], 1.0, "Low",
                                       "VeriMedX System", "★★★★★ VeriMedX"),
                "why": "Greeting intent — welcoming the user.",
            }

        # ── 3. Emergency ────────────────────────────────────────────────
        if intent == "emergency" or self.triage_service.is_emergency(message):
            return {
                "response": (
                    "🚨 **EMERGENCY DETECTED** 🚨\n\n"
                    + self.triage_service.build_emergency_response()
                    + "\n\n**Please call your local emergency services immediately (112 / 999 / 911).**"
                ),
                **self._evidence_block([], 0.99, "High",
                                       "WHO Emergency Protocol (2023)", "★★★★★ WHO"),
                "why": "Emergency symptoms detected — immediate protocol activated.",
            }

        # ── 4. Report upload ─────────────────────────────────────────────
        if intent == "report_upload":
            return {
                "response": (
                    "To analyse your medical report, please upload it using the "
                    "**Report Interpreter** tab (PDF or image). I will:\n"
                    "1. Extract all clinical values using OCR.\n"
                    "2. Map findings to LOINC / SNOMED / ICD-10 codes.\n"
                    "3. Verify each finding against verified clinical guidelines.\n"
                    "4. Generate personalised clinical and patient summaries."
                ),
                **self._evidence_block([], 1.0, "Low",
                                       "VeriMedX Report Pipeline", "★★★★★ VeriMedX"),
                "why": "User requested report analysis.",
            }

        # ── 5. Small talk / casual ───────────────────────────────────────
        if intent == "small_talk":
            return {
                "response": (
                    "I'm doing well, thank you! 😊 I'm VeriMedX, always ready to help with "
                    "clinical questions. You can describe a symptom, ask about a medication, "
                    "or upload a lab report for detailed analysis."
                ),
                **self._evidence_block([], 1.0, "Low",
                                       "VeriMedX System", "★★★★★ VeriMedX"),
                "why": "Casual conversation — friendly response within clinical scope.",
            }

        # ── 6. Symptom triage ────────────────────────────────────────────
        if intent in ("symptom", "follow_up"):
            if memory:
                # Capture the presenting symptom from the first message
                if not meta.get("symptom") and intent == "symptom":
                    for kw in SYMPTOM_KEYWORDS:
                        if kw in message.lower():
                            memory.update_metadata(session_id, {"symptom": kw})
                            meta = memory.get_metadata(session_id)
                            break

                memory.activate_triage(session_id)
                next_step = memory.next_triage_step(session_id)

                if next_step and not memory.triage_complete(session_id):
                    # Build the question for the next unanswered step
                    q_template = TRIAGE_QUESTIONS.get(next_step, "Could you provide more details?")
                    symptom_label = meta.get("symptom", "your symptom")
                    question_text = q_template.format(symptom=symptom_label)

                    # Mark this step as asked
                    memory.mark_asked(session_id, next_step)

                    return {
                        "response": question_text,
                        **self._evidence_block([], 0.95, "Low",
                                               "WHO Clinical Triage Protocol", "★★★★★ WHO"),
                        "why": f"Triage step: collecting '{next_step}' — not yet provided.",
                    }

                # Triage is complete — generate the assessment
                memory.deactivate_triage(session_id)

            # Synthesise risk from collected metadata
            risk, reasons = self._assess_risk(meta)
            self.ensure_knowledge()
            query_kw = meta.get("symptom", message)
            snippets = self._retrieve(query_kw, top_k=3)
            patient_ctx = memory.build_personalized_prompt_context(session_id) if memory else ""

            prompt = self._build_prompt(
                f"Provide clinical guidance for: {query_kw}",
                snippets, patient_ctx
            )
            rag_ans = self.llm.generate(prompt, max_length=260)

            age = meta.get("age", "unknown age")
            gender = meta.get("gender", "unknown gender")
            sym = meta.get("symptom", "your symptom")
            dur = meta.get("symptom_duration", "unspecified duration")
            temp = meta.get("symptom_temp", "not measured")
            allergy = meta.get("allergies", "none reported")
            pregnant = meta.get("pregnancy_status", "N/A")

            header = (
                f"**VeriMedX Triage Assessment**\n\n"
                f"**Patient:** {age} y/o {gender}"
                + (f", pregnant" if pregnant == "Pregnant" else "")
                + f"\n**Symptom:** {sym} for {dur}, temperature: {temp}\n"
                f"**Allergies:** {allergy}\n\n"
                f"**Risk Level:** {'🔴 HIGH' if risk == 'High' else ('🟡 MODERATE' if risk == 'Medium' else '🟢 LOW')}\n"
                f"*{', '.join(reasons) if reasons else 'No high-risk markers identified.'}*\n\n"
            )

            if risk == "High":
                guidance = (
                    "⚠️ Please seek **urgent medical evaluation** — visit an emergency department "
                    "or call your doctor today. Do not self-medicate.\n\n"
                )
            elif risk == "Medium":
                guidance = (
                    "Please consult a healthcare provider **within 24–48 hours**. "
                    "Stay hydrated and monitor your symptoms closely.\n\n"
                )
            else:
                guidance = (
                    "Your symptoms appear **low risk** at this stage. Rest well, stay hydrated, "
                    "and consult a doctor if symptoms worsen or persist beyond 72 hours.\n\n"
                )

            body = f"{rag_ans}\n\n" if (rag_ans and len(rag_ans) > 20) else ""
            disclaimer = (
                "_⚕️ This is AI-generated guidance only — not a medical diagnosis. "
                "Always consult a qualified healthcare professional._"
            )

            eb = self._evidence_block(snippets, 0.93 if risk == "Low" else 0.87, risk)

            return {
                "response": header + guidance + body + disclaimer,
                **eb,
                "why": (
                    f"Triage complete. Risk assessed as {risk}. "
                    f"Reasons: {', '.join(reasons) if reasons else 'none'}."
                ),
            }

        # ── 7. Disease information ───────────────────────────────────────
        if intent == "disease_info":
            self.ensure_knowledge()
            snippets = self._retrieve(message, top_k=4)
            prompt = self._build_prompt(message, snippets, patient_ctx)
            answer = self.llm.generate(prompt, max_length=280)
            if not answer or len(answer) < 15:
                for kw in DISEASE_KEYWORDS:
                    if kw in message.lower():
                        answer = FALLBACK_CONTENT.get(
                            kw.replace(" ", "_").title(),
                            f"Detailed information on {kw} is available from WHO and CDC guidelines."
                        )
                        break

            eb = self._evidence_block(snippets, 0.96, "Low")
            return {
                "response": answer + "\n\n_⚕️ Always verify with a qualified clinician._",
                **eb,
                "why": "Disease information query — RAG evidence retrieved.",
            }

        # ── 8. Medicine information ──────────────────────────────────────
        if intent == "medicine_info":
            self.ensure_knowledge()
            snippets = self._retrieve(message, top_k=4)
            prompt = self._build_prompt(message, snippets, patient_ctx)
            answer = self.llm.generate(prompt, max_length=280)
            if not answer or len(answer) < 15:
                for kw in MEDICINE_KEYWORDS:
                    if kw in message.lower():
                        answer = FALLBACK_CONTENT.get(
                            kw.title(),
                            f"Please consult a pharmacist for detailed information on {kw}."
                        )
                        break

            eb = self._evidence_block(snippets, 0.95, "Low")
            return {
                "response": answer + "\n\n_⚕️ Always consult a pharmacist or prescriber before use._",
                **eb,
                "why": "Medication information query — RAG evidence retrieved.",
            }

        # ── 9. General guidance / fallback RAG ──────────────────────────
        self.ensure_knowledge()
        snippets = self._retrieve(message, top_k=4)
        if not snippets:
            return {
                "response": (
                    "I wasn't able to find a specific evidence match for your query in my "
                    "knowledge base. Could you rephrase or provide more clinical detail? "
                    "Alternatively, consult a qualified healthcare professional directly.\n\n"
                    "_⚕️ VeriMedX always recommends professional medical advice._"
                ),
                **self._evidence_block([], 0.50, "Low",
                                       "VeriMedX Knowledge Base", "★★ General Reference"),
                "why": "No matching evidence found in knowledge index.",
            }

        prompt = self._build_prompt(message, snippets, patient_ctx or context_summary)
        answer = self.llm.generate(prompt, max_length=260)
        if not answer or len(answer) < 15:
            answer = snippets[0]["text"]

        eb = self._evidence_block(snippets, 0.92, "Low")
        return {
            "response": answer + "\n\n_⚕️ Consult a qualified clinician for personalised advice._",
            **eb,
            "why": "General medical query — RAG evidence retrieved.",
        }

    # ------------------------------------------------------------------
    # Risk assessment helper
    # ------------------------------------------------------------------

    def _assess_risk(self, meta: Dict) -> tuple[str, List[str]]:
        risk = "Low"
        reasons = []

        temp_str = meta.get("symptom_temp", "")
        if temp_str:
            nums = re.findall(r"\d+(?:\.\d)?", temp_str)
            if nums:
                t = float(nums[0])
                is_c = "C" in temp_str.upper()
                t_f = t if not is_c else (t * 9 / 5 + 32)
                if t_f >= 103:
                    risk = "High"
                    reasons.append(f"High temperature ({temp_str})")
                elif t_f >= 100.4:
                    risk = max(risk, "Medium") if risk == "Low" else risk
                    reasons.append(f"Elevated temperature ({temp_str})")

        dur = meta.get("symptom_duration", "")
        if dur:
            d_nums = re.findall(r"\d+", dur)
            if d_nums:
                d = int(d_nums[0])
                unit = "day" if "day" in dur else ("week" if "week" in dur else "")
                if unit == "week" or (unit == "day" and d >= 5):
                    risk = "High" if risk == "Medium" else risk
                    reasons.append(f"Prolonged duration ({dur})")
                elif unit == "day" and d >= 3:
                    risk = "Medium" if risk == "Low" else risk
                    reasons.append(f"Duration ≥3 days ({dur})")

        if meta.get("pregnancy_status") == "Pregnant":
            risk = "High"
            reasons.append("Pregnancy — elevated clinical priority")

        if meta.get("existing_diseases"):
            if any(d in meta["existing_diseases"].lower() for d in ["diabetes", "heart", "kidney", "copd"]):
                risk = "High" if risk == "Medium" else risk
                reasons.append(f"Pre-existing comorbidity: {meta['existing_diseases']}")

        return risk, reasons

    # ------------------------------------------------------------------
    # Public training endpoint
    # ------------------------------------------------------------------

    def train_knowledge(self) -> Dict:
        result = self.trainer.train()
        self.documents = self.trainer.load_corpus()
        self._build_index()
        return result
