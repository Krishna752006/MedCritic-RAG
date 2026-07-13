class EvidenceTierEvaluator:
    @staticmethod
    def get_tier_level(source_name: str) -> str:
        """
        Classifies guideline source clinical tiers.
        """
        s_upper = source_name.upper().strip()
        if any(src in s_upper for src in ["WHO", "CDC", "NICE", "ADA", "ACC", "AHA", "FDA", "EMA"]):
            return "Tier 1: Strong (Official Global/National Guidelines)"
        elif any(src in s_upper for src in ["AACE", "ESC", "NIDDK", "ACR", "IDSA"]):
            return "Tier 2: Moderate (Specialist Society Consensus)"
        else:
            return "Tier 3: Weak (Individual Clinical Trials / Observational Studies)"
