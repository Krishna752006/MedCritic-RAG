from src.recommendation.decision_support import ClinicalDecisionSupport


class RecommendationService:
    def __init__(self):
        self.decision_support = ClinicalDecisionSupport()

    def assess(self, message: str, sources: list):
        return self.decision_support.assess(message, sources)

