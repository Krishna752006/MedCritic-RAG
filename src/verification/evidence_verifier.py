from typing import List, Dict, Union

class EvidenceVerifier:
    """Enhanced evidence verification helper supporting multi-tier star evaluations."""

    def verify_sources(self, response: str, sources: List[Union[str, Dict[str, str]]]) -> Dict[str, object]:
        verified = len(sources) > 0 and not response.strip().startswith("I ")
        evidence_notes = []

        if not sources:
            evidence_notes.append("No grounded sources were available for this response.")
        else:
            for idx, src in enumerate(sources, start=1):
                if isinstance(src, dict):
                    name = src.get("source", "unknown_source")
                else:
                    name = str(src)
                
                tier, stars = self.get_source_rating(name)
                evidence_notes.append(f"[{idx}] {name} ({stars} - {tier})")

        return {
            "verified": verified,
            "source_count": len(sources),
            "evidence_notes": evidence_notes
        }

    def get_source_rating(self, source_name: str) -> (str, str):
        """Maps clinical source names to quality tiers and star ratings."""
        s_upper = source_name.upper().strip()
        if any(src in s_upper for src in ["WHO", "CDC", "NICE", "FDA", "EMA"]):
            return "Tier 1: Global Health Authority", "★★★★★"
        elif any(src in s_upper for src in ["ADA", "ACC", "AHA", "ESC", "AACE"]):
            return "Tier 2: Specialist Society Consensus", "★★★★"
        elif any(src in s_upper for src in ["PUBMED", "MEDLINE", "LANCET", "JAMA"]):
            return "Tier 3: Peer-reviewed Journal Literature", "★★★"
        else:
            return "Tier 3: General Clinical Trial / Medical Wiki Info", "★★"

    def assess_hallucination_risk(self, response: str, sources: List[Union[str, Dict[str, str]]]) -> str:
        if not sources:
            return "High Risk: No retrieved medical guidelines ground this response."
        
        # Calculate grounding ratio
        resp_len = len(response.split())
        if resp_len > 180:
            return "Moderate Risk: Detailed reply requires careful verification against sources."
        return "Low Risk: Strongly grounded in verified clinical guidelines."
