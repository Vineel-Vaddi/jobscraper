import logging

logger = logging.getLogger(__name__)

class DiffEngine:
    @staticmethod
    def compute_diff(base_profile: dict, tailored_profile: dict) -> list:
        """
        Computes a simplistic deterministic diff between the Canonical Profile 
        and the structured Tailored JSON output.
        """
        logger.info("Computing diff between master profile and tailored variant.")
        section_diffs = []
        
        # 1. Summary Diff
        base_summary = base_profile.get("summary", {}).get("summary_text", "")
        tailored_summary = tailored_profile.get("summary", {}).get("summary_text", "")
        
        status = "unchanged"
        if base_summary != tailored_summary:
            status = "modified"
        
        section_diffs.append({
            "section_name": "Summary",
            "status": status,
            "bullets": [
                {"text": tailored_summary, "type": "rewritten" if status == "modified" else "unchanged"}
            ]
        })
            
        # 2. Skills Diff
        base_skills = set(base_profile.get("skills", []))
        tailored_skills_list = tailored_profile.get("skills", [])
        tailored_skills = set(tailored_skills_list)
        
        skill_status = "unchanged"
        if base_skills != tailored_skills or base_profile.get("skills", []) != tailored_skills_list:
            skill_status = "modified"
            
        skill_bullets = []
        for s in tailored_skills_list:
            if s not in base_skills:
                skill_bullets.append({"text": s, "type": "added"})
            else:
                skill_bullets.append({"text": s, "type": "unchanged"}) # reordered if positions changed, but keeping it simple
                
        section_diffs.append({
            "section_name": "Technical Skills",
            "status": skill_status,
            "bullets": skill_bullets
        })
        
        # 3. Experience Diff
        # Will iterate over tailored, flag if missing from base, compare bullets
        base_exp = {e.get("title", "") + e.get("company", ""): e for e in base_profile.get("experience", [])}
        
        for exp in tailored_profile.get("experience", []):
            key = exp.get("title", "") + exp.get("company", "")
            bullets = exp.get("bullets", [])
            
            exp_status = "unchanged"
            bullet_diffs = []
            
            if key in base_exp:
                base_bullets = base_exp[key].get("bullets", [])
                
                # Check for reorders, additions, logic deletions.
                # Since we strictly preserve and just reorder, most will be unchanged.
                for b in bullets:
                    if b in base_bullets:
                        bullet_diffs.append({"text": b, "type": "unchanged"})
                    else:
                        bullet_diffs.append({"text": b, "type": "rewritten"})
                        exp_status = "modified"
            else:
                exp_status = "added"
                bullet_diffs = [{"text": b, "type": "added"} for b in bullets]
                
            section_diffs.append({
                "section_name": f"Experience: {exp.get('title')} at {exp.get('company')}",
                "status": exp_status,
                "bullets": bullet_diffs
            })

        return section_diffs
