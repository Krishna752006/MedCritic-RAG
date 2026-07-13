class ResponseBuilder:
    def build(self, intent: str, task: str, payload: dict) -> dict:
        return {
            "intent": intent,
            "task": task,
            "response": payload["response"],
            "sources": payload.get("sources", []),
            "why": payload.get("why"),
            "evidence": payload.get("evidence"),
            "source": payload.get("source"),
            "confidence": payload.get("confidence", 0.95),
            "evidence_ranking": payload.get("evidence_ranking", "General Reference"),
            "health_risk_score": payload.get("health_risk_score", "Low"),
        }

