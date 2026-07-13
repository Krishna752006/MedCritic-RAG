from typing import List
from src.extraction.schema import VerificationEvidence

class ConfidenceCalibrator:
    @staticmethod
    def calculate(evidences: List[VerificationEvidence]) -> float:
        """
        Calibrates global answer confidence by weighting NLI status flags.
        Formula:
          Verified = Weight 1.0
          Contradicted = Weight 0.0
          Unverified = Weight 0.4
        """
        if not evidences:
            return 0.50

        total_weight = 0.0
        for ev in evidences:
            if ev.status == "Verified":
                total_weight += 1.0 * ev.strength_score
            elif ev.status == "Unverified":
                total_weight += 0.4 * ev.strength_score
            elif ev.status == "Contradicted":
                total_weight += 0.0
                
        # Average weight calibrated to bounded range [0.1, 0.99]
        avg_score = total_weight / len(evidences)
        calibrated = 0.10 + 0.89 * avg_score
        return round(float(calibrated), 2)
