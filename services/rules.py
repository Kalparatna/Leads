def calculate_rule_score(lead, offer):
    """
    Calculate rule-based score for a lead (max 50 points)
    
    Args:
        lead (dict): Lead information
        offer (dict): Offer/product information
    
    Returns:
        int: Rule-based score (0-50)
    """
    score = 0

    # Role relevance (0-20 points)
    role = (lead.get("role") or "").lower()
    
    # Decision maker roles (+20 points)
    decision_maker_keywords = [
        "ceo", "cto", "cfo", "coo", "chief", "founder", "president", 
        "head of", "vp", "vice president", "director"
    ]
    
    # Influencer roles (+10 points)
    influencer_keywords = [
        "manager", "lead", "senior", "principal", "team lead"
    ]
    
    if any(keyword in role for keyword in decision_maker_keywords):
        score += 20
    elif any(keyword in role for keyword in influencer_keywords):
        score += 10

    # Industry match (0-20 points)
    industry = (lead.get("industry") or "").lower()
    ideal_use_cases = offer.get("ideal_use_cases", [])
    
    # Convert ideal use cases to lowercase for matching
    icp_keywords = []
    for use_case in ideal_use_cases:
        icp_keywords.extend(use_case.lower().split())
    
    # Exact ICP match (+20 points)
    if any(keyword in industry for keyword in icp_keywords):
        score += 20
    # Adjacent industry match (+10 points)
    elif any(word in industry for word in ["tech", "technology", "software", "b2b", "saas"]):
        score += 10

    # Data completeness (0-10 points)
    required_fields = ["name", "role", "company", "industry", "location", "linkedin_bio"]
    if all(lead.get(field) and str(lead.get(field)).strip() for field in required_fields):
        score += 10

    return min(score, 50)  # Ensure max score is 50
