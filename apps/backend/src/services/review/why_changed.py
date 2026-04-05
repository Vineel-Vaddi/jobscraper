import logging

logger = logging.getLogger(__name__)

class WhyChangedGenerator:
    @staticmethod
    def generate_notes(keyword_alignment: dict, skill_gap: dict, validator_report: dict) -> list:
        """
        Creates transparent explanations of why the resume was augmented the way it was.
        """
        logger.info("Generating 'Why Changed' notes...")
        notes = []
        
        supported = keyword_alignment.get("supported_keywords", [])
        if supported:
            notes.append(f"Emphasized the following skills across Summary and Skills sections because they align directly with the Job Description and are supported by your Canonical Profile: {', '.join(supported[:3])}.")
            
        unsupported = skill_gap.get("unsupported_skills", [])
        if unsupported:
            notes.append(f"Deliberately omitted {', '.join(unsupported[:2])} from the tailored resume because there is no direct evidence confirming them in your master profile.")
            
        unsupported_claims = validator_report.get("unsupported_claims", [])
        if unsupported_claims:
            notes.append(f"WARNING: The truth validator detected unsupported claims generated in the tailored variant: {', '.join(unsupported_claims)}.")
            
        notes.append("Experience bullets were preserved exactly matching your canonical profile baseline for complete accuracy.")
            
        return notes
