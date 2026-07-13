import re
from collections import defaultdict
from typing import Dict, List, Optional


class ConversationMemory:
    """
    VeriMedX session memory: stores dialogue history, patient metadata,
    and tracks which triage questions have already been asked so they
    are NEVER repeated in the same session.
    """

    # The ordered list of triage steps VeriMedX needs to complete
    TRIAGE_STEPS = [
        "symptom",
        "symptom_duration",
        "symptom_temp",    # only for fever
        "age",
        "gender",
        "pregnancy_status",  # only for Female, age 15-50
        "allergies",
        "existing_diseases",
    ]

    def __init__(self):
        self.memory_store: Dict[str, List[Dict[str, str]]] = defaultdict(list)
        self.metadata_store: Dict[str, Dict] = defaultdict(self._default_meta)
        # Tracks which triage steps have been *asked* (not necessarily answered)
        self.asked_steps: Dict[str, set] = defaultdict(set)
        # Tracks whether the triage workflow is currently active
        self.triage_active: Dict[str, bool] = defaultdict(bool)

    @staticmethod
    def _default_meta() -> Dict:
        return {
            "age": None,
            "gender": None,
            "pregnancy_status": None,
            "allergies": None,
            "existing_diseases": None,
            "symptom": None,
            "symptom_duration": None,
            "symptom_temp": None,
            "other_symptoms": None,
            "uploaded_reports": [],
            "previous_findings": [],
            "active_medications": [],
            "user_preferences": {},
        }

    # ------------------------------------------------------------------
    # Core memory operations
    # ------------------------------------------------------------------

    def add_message(self, session_id: str, role: str, text: str) -> None:
        self.memory_store[session_id].append({"role": role, "text": text})
        if role == "user":
            self._parse_metadata(session_id, text)

    def mark_asked(self, session_id: str, step: str) -> None:
        """Record that a triage question for this step was already sent."""
        self.asked_steps[session_id].add(step)

    def was_asked(self, session_id: str, step: str) -> bool:
        """Return True if this triage step question has already been sent."""
        return step in self.asked_steps[session_id]

    def activate_triage(self, session_id: str) -> None:
        self.triage_active[session_id] = True

    def is_triage_active(self, session_id: str) -> bool:
        return self.triage_active.get(session_id, False)

    def deactivate_triage(self, session_id: str) -> None:
        self.triage_active[session_id] = False

    def get_history(self, session_id: str, limit: int = 14) -> List[Dict[str, str]]:
        return self.memory_store.get(session_id, [])[-limit:]

    def get_metadata(self, session_id: str) -> Dict:
        return self.metadata_store[session_id]

    def update_metadata(self, session_id: str, updates: Dict) -> None:
        for k, v in updates.items():
            if v is not None:
                self.metadata_store[session_id][k] = v

    def clear_session(self, session_id: str) -> None:
        self.memory_store.pop(session_id, None)
        self.metadata_store.pop(session_id, None)
        self.asked_steps.pop(session_id, None)
        self.triage_active.pop(session_id, None)

    # ------------------------------------------------------------------
    # Triage step resolution — returns the NEXT unanswered, unasked step
    # ------------------------------------------------------------------

    def next_triage_step(self, session_id: str) -> Optional[str]:
        """
        Returns the next triage step that (a) has not been answered yet
        AND (b) is applicable given current context.
        Returns None when triage is complete.
        """
        meta = self.get_metadata(session_id)

        for step in self.TRIAGE_STEPS:
            # Skip steps already answered
            if meta.get(step) is not None:
                continue

            # Contextual skip rules
            if step == "symptom_temp" and meta.get("symptom") not in (
                "fever", "temperature", "pyrexia", "high fever"
            ):
                continue
            if step == "pregnancy_status":
                if meta.get("gender") != "Female":
                    continue
                age = meta.get("age")
                if age is not None and (age < 13 or age > 55):
                    continue

            # Return the next unanswered step (even if already asked —
            # the chat service decides whether to re-ask or wait)
            return step

        return None  # All relevant steps answered → triage complete

    def triage_complete(self, session_id: str) -> bool:
        return self.next_triage_step(session_id) is None

    # ------------------------------------------------------------------
    # Automatic metadata extraction from user messages
    # ------------------------------------------------------------------

    def _parse_metadata(self, session_id: str, text: str) -> None:
        meta = self.metadata_store[session_id]
        tl = text.lower()

        # Temperature — e.g. "102F", "38.5 C", "39 degrees"
        temp_match = re.search(r"\b(\d{2,3}(?:\.\d)?)\s*(?:degrees?|deg|°)?\s*(c|f)\b", tl)
        if temp_match and not meta["symptom_temp"]:
            val, unit = temp_match.groups()
            meta["symptom_temp"] = f"{val}°{unit.upper()}"
        else:
            num_match = re.search(r"\b(9[7-9]|10[0-6])(?:\.\d)?\b", tl)
            if num_match and not meta["symptom_temp"]:
                meta["symptom_temp"] = f"{num_match.group(0)}°F"

        # Age — "I am 32", "35 years old", "age: 40", short digit reply
        age_match = re.search(
            r"\b(?:i am|i'm|age is|age:)?\s*(\d{1,2})\s*(?:years?|yrs?|yo|y\.o\.)\b", tl
        )
        if age_match and not meta["age"]:
            meta["age"] = int(age_match.group(1))
        elif not meta["age"]:
            digits = re.findall(r"\b(\d{1,3})\b", tl)
            if digits:
                history = self.get_history(session_id)
                if history:
                    last_assistant = next(
                        (h["text"].lower() for h in reversed(history) if h["role"] == "assistant"),
                        ""
                    )
                    if any(kw in last_assistant for kw in ["old are you", "your age", "how old"]):
                        candidate = int(digits[0])
                        if 1 <= candidate <= 120:
                            meta["age"] = candidate

        # Duration — "3 days", "since yesterday", "for a week"
        dur_match = re.search(
            r"\b(?:for|since|about|almost|last)?\s*(\d+)\s*(days?|hours?|weeks?|months?)\b", tl
        )
        if dur_match and not meta["symptom_duration"]:
            meta["symptom_duration"] = f"{dur_match.group(1)} {dur_match.group(2)}"
        elif not meta["symptom_duration"] and "yesterday" in tl:
            meta["symptom_duration"] = "1 day"

        # Pregnancy
        if "pregnant" in tl or "pregnancy" in tl:
            meta["pregnancy_status"] = "Not Pregnant" if "not pregnant" in tl else "Pregnant"
        elif tl.strip() in ("no", "nope", "no i'm not", "i am not"):
            # Short denial in context of last question about pregnancy
            history = self.get_history(session_id)
            if history:
                last = next(
                    (h["text"].lower() for h in reversed(history) if h["role"] == "assistant"), ""
                )
                if "pregnant" in last:
                    meta["pregnancy_status"] = "Not Pregnant"
        elif "yes" in tl.split() or tl.strip() == "yes":
            history = self.get_history(session_id)
            if history:
                last = next(
                    (h["text"].lower() for h in reversed(history) if h["role"] == "assistant"), ""
                )
                if "pregnant" in last:
                    meta["pregnancy_status"] = "Pregnant"

        # Gender
        g_match = re.search(r"\b(male|female|man|woman|boy|girl)\b", tl)
        if g_match and not meta["gender"]:
            word = g_match.group(1)
            meta["gender"] = "Female" if word in ("female", "woman", "girl") else "Male"

        # Allergies — "no allergies", "none", "penicillin"
        history = self.get_history(session_id)
        if not meta["allergies"] and history:
            last = next(
                (h["text"].lower() for h in reversed(history) if h["role"] == "assistant"), ""
            )
            if "allerg" in last:
                if tl.strip() in ("none", "no", "no allergies", "i have none", "nothing"):
                    meta["allergies"] = "None"
                elif len(tl.split()) <= 6:
                    meta["allergies"] = text.strip()

        # Existing diseases — "I have diabetes", "hypertension"
        disease_kws = ["diabetes", "hypertension", "asthma", "heart", "kidney", "copd",
                       "epilepsy", "cancer", "arthritis", "thyroid", "hiv", "hepatitis"]
        if not meta["existing_diseases"]:
            found = [d for d in disease_kws if d in tl]
            if found:
                meta["existing_diseases"] = ", ".join(found)

    # ------------------------------------------------------------------
    # Context builders
    # ------------------------------------------------------------------

    def build_personalized_prompt_context(self, session_id: str) -> str:
        meta = self.get_metadata(session_id)
        parts = []

        demo = []
        if meta["age"]:
            demo.append(f"{meta['age']} years old")
        if meta["gender"]:
            demo.append(meta["gender"])
        if meta["pregnancy_status"] == "Pregnant":
            demo.append("currently pregnant")
        if demo:
            parts.append(f"Patient profile: {', '.join(demo)}.")

        if meta["allergies"] and meta["allergies"] != "None":
            parts.append(f"Known allergies: {meta['allergies']}.")
        if meta["existing_diseases"]:
            parts.append(f"Pre-existing conditions: {meta['existing_diseases']}.")
        if meta.get("active_medications"):
            parts.append(f"Active medications: {', '.join(meta['active_medications'])}.")
        if meta.get("previous_findings"):
            parts.append(f"Previous findings available: {len(meta['previous_findings'])}.")
        if meta.get("uploaded_reports"):
            parts.append(f"Uploaded reports available: {len(meta['uploaded_reports'])}.")
        if meta.get("user_preferences"):
            parts.append(f"User preferences: {meta['user_preferences']}.")

        symp = []
        if meta["symptom"]:
            symp.append(f"symptom: {meta['symptom']}")
        if meta["symptom_duration"]:
            symp.append(f"duration: {meta['symptom_duration']}")
        if meta["symptom_temp"]:
            symp.append(f"temperature: {meta['symptom_temp']}")
        if symp:
            parts.append(f"Presenting complaint: {', '.join(symp)}.")

        return " ".join(parts)

    def summarize_history(self, session_id: str, max_chars: int = 900) -> Optional[str]:
        history = self.get_history(session_id)
        if not history:
            return None
        summary = " | ".join(f"{h['role']}: {h['text']}" for h in history)
        return summary[:max_chars]
