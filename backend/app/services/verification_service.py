from src.verification.confidence import ConfidenceCalibrator
from src.verification.critic_verifier import CriticVerifier
from src.verification.evidence_verifier import EvidenceVerifier


class VerificationService:
    def __init__(self):
        self.critic = CriticVerifier()
        self.evidence = EvidenceVerifier()

    def verify_findings(self, findings, guidelines):
        verifications = self.critic.verify_findings(findings, guidelines)
        confidence = ConfidenceCalibrator.calculate(verifications)
        return verifications, confidence

