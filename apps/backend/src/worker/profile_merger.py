from typing import List, Dict, Any

# Precedence scale (higher is better)
DOCUMENT_TYPE_PRECEDENCE = {
    "linkedin_export": 3,
    "linkedin_pdf": 2,
    "resume": 1,
    "unknown": 0
}

def merge_profiles(profiles_input: List[Dict[str, Any]]) -> tuple[Dict[str, Any], Dict[str, Any]]:
    """
    profiles_input structure:
    [
        {
            "document_id": int,
            "document_type": str,
            "json": dict (the output of semantic parser)
        }
    ]
    Returns a tuple: (merged_profile_json, confidence_summary_json)
    """
    
    merged = {
        "identity": {},
        "headline": "",
        "summary": "",
        "skills": [],
        "experience": [],
        "education": [],
        "projects": [],
        "certifications": [],
        "links": [],
        "metadata": {
            "source_documents": [],
            "profile_confidence": 0.0
        }
    }
    
    confidence_summary = {
        "conflicts_resolved": 0,
        "section_provenance": {}
    }
    
    if not profiles_input:
        return merged, confidence_summary
        
    # Sort by precedence descending
    profiles_input.sort(key=lambda x: DOCUMENT_TYPE_PRECEDENCE.get(x["document_type"], 0), reverse=True)
    
    merged["metadata"]["source_documents"] = [p["document_id"] for p in profiles_input]
    
    # Track provenance
    provenance = {}
    
    for profile_doc in profiles_input:
        doc_id = profile_doc["document_id"]
        source_json = profile_doc["json"]
        
        # Merge Identity (First wins due to sorting)
        if "identity" in source_json and isinstance(source_json["identity"], dict):
            for k, v in source_json["identity"].items():
                if v and not merged["identity"].get(k):
                    merged["identity"][k] = v
                    provenance[f"identity.{k}"] = doc_id
                    
        # Headline & Summary
        if source_json.get("headline") and not merged["headline"]:
            merged["headline"] = source_json["headline"]
            provenance["headline"] = doc_id
        if source_json.get("summary") and not merged["summary"]:
            merged["summary"] = source_json["summary"]
            provenance["summary"] = doc_id
            
        # Merge Skills (Union)
        if isinstance(source_json.get("skills"), list):
            for skill in source_json["skills"]:
                if isinstance(skill, str):
                    skill_cleaned = skill.strip()
                    if skill_cleaned.lower() not in [s.lower() for s in merged["skills"]]:
                        merged["skills"].append(skill_cleaned)
                        
        # Merge Experience
        # Basic Strategy: Since sorted by precedence, we append, but check if same company/title exist
        if isinstance(source_json.get("experience"), list):
            for exp in source_json["experience"]:
                # simple duplicate check
                is_dup = False
                for existing in merged["experience"]:
                    if existing.get("company", "").lower() == exp.get("company", "").lower() and \
                       existing.get("title", "").lower() == exp.get("title", "").lower():
                        is_dup = True
                        confidence_summary["conflicts_resolved"] += 1
                        # We could merge bullets, but for now we keep the higher precedence one
                        break
                
                if not is_dup:
                    exp["source_refs"] = [doc_id]
                    merged["experience"].append(exp)
                    
        # Merge Education
        if isinstance(source_json.get("education"), list):
            for edu in source_json["education"]:
                is_dup = False
                for existing in merged["education"]:
                    if existing.get("institution", "").lower() == edu.get("institution", "").lower():
                        is_dup = True
                        confidence_summary["conflicts_resolved"] += 1
                        break
                if not is_dup:
                    edu["source_refs"] = [doc_id]
                    merged["education"].append(edu)
                    
    confidence_summary["section_provenance"] = provenance
    merged["metadata"]["profile_confidence"] = 0.9 if profiles_input else 0.0 # basic heuristic
    
    return merged, confidence_summary
