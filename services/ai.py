import os
import json
import re
import requests
from typing import Tuple

# -------------------------
# Environment variables
# -------------------------
AI_PROVIDER = os.getenv("AI_PROVIDER", "mock").lower()
GEMINI_API_KEY = os.getenv("VERTEX_API_KEY")  
GOOGLE_PROJECT = os.getenv("PROJECT_ID")     
GOOGLE_LOCATION = os.getenv("GOOGLE_LOCATION", "us-central1")
MODEL = os.getenv("MODEL", "publishers/google/models/gemini-2.5-flash")

REQUEST_TIMEOUT = int(os.getenv("AI_REQUEST_TIMEOUT_SECONDS", "20"))

# -------------------------
# Helper functions
# -------------------------
def _build_prompt(lead: dict, offer: dict) -> str:
    lead_block = json.dumps({
        "name": lead.get("name"),
        "role": lead.get("role"),
        "company": lead.get("company"),
        "industry": lead.get("industry"),
        "location": lead.get("location"),
        "linkedin_bio": lead.get("linkedin_bio")
    }, ensure_ascii=False)
    offer_block = json.dumps({
        "name": offer.get("name"),
        "value_props": offer.get("value_props"),
        "ideal_use_cases": offer.get("ideal_use_cases")
    }, ensure_ascii=False)

    return (
        f"Offer:\n{offer_block}\n\n"
        f"Lead:\n{lead_block}\n\n"
        "Task: Classify buying intent as High/Medium/Low and provide 1-2 sentence reasoning. "
        "Respond in 1 line with the label first followed by reasoning."
    )

def _parse_label_and_reasoning(text: str) -> Tuple[str, str]:
    if not text:
        return "Medium", "No response from model; default to Medium."
    m = re.search(r"\b(High|Medium|Low)\b", text, flags=re.IGNORECASE)
    label = m.group(1).capitalize() if m else "Medium"
    reasoning = re.sub(r"^\s*(High|Medium|Low)\s*[:\-\u2014]?\s*", "", text.strip(), flags=re.IGNORECASE).strip()
    if len(reasoning) > 350:
        reasoning = reasoning[:347] + "..."
    if not reasoning:
        reasoning = "No explanation provided."
    return label, reasoning

# -------------------------
# Mock AI (fallback)
# -------------------------
def mock_ai(lead: dict, offer: dict) -> Tuple[str, str]:
    role = (lead.get("role") or "").lower()
    industry = (lead.get("industry") or "").lower()
    bio = (lead.get("linkedin_bio") or "").lower()
    icp_text = " ".join(offer.get("ideal_use_cases") or []).lower()

    if any(k in role for k in ["ceo", "founder", "cto", "cxo", "head", "vp", "director"]):
        if "saas" in industry or "saas" in icp_text or "software" in industry:
            return "High", "Decision-maker at an organization matching ICP (SaaS/software)."
        return "High", "Senior decision-maker role detected."
    if any(k in role for k in ["manager", "lead", "senior"]):
        if "saas" in industry or "b2b" in industry or "software" in industry or "saas" in icp_text:
            return "Medium", "Mid-level role in relevant industry; may influence purchasing decisions."
        return "Medium", "Relevant role, but not a confirmed decision-maker."
    if any(k in bio for k in ["growth", "sales", "revops", "outreach", "marketing"]):
        return "Medium", "Role or bio mentions growth/marketing—may be receptive to outreach."
    return "Low", "No strong signals in role, industry or bio."

# -------------------------
# Vertex via API key
# -------------------------
def _call_vertex_api_key(prompt: str) -> dict:
    if not GEMINI_API_KEY or not GOOGLE_PROJECT:
        raise RuntimeError("VERTEX_API_KEY and PROJECT_ID must be set for vertex_api_key provider.")

    endpoint = (
        f"https://{GOOGLE_LOCATION}-aiplatform.googleapis.com/v1/projects/{GOOGLE_PROJECT}"
        f"/locations/{GOOGLE_LOCATION}/{MODEL}:predict?key={GEMINI_API_KEY}"
    )

    body = {
        "instances": [{"content": prompt}],
        "parameters": {"temperature": 0.0, "maxOutputTokens": 256}
    }
    resp = requests.post(endpoint, json=body, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.json()

# -------------------------
# Public AI function
# -------------------------
def ai_classify(lead: dict, offer: dict) -> Tuple[str, str, int]:
    provider = AI_PROVIDER
    prompt = _build_prompt(lead, offer)

    try:
        if provider == "mock":
            label, reasoning = mock_ai(lead, offer)
        elif provider == "vertex_api_key":
            resp_json = _call_vertex_api_key(prompt)
            text_output = ""
            preds = resp_json.get("predictions") or []
            if preds and isinstance(preds, list):
                p0 = preds[0]
                if isinstance(p0, dict) and "content" in p0:
                    text_output = p0["content"]
                else:
                    text_output = str(p0)
            if not text_output:
                text_output = json.dumps(resp_json)
            label, reasoning = _parse_label_and_reasoning(text_output)
        else:
            label, reasoning = mock_ai(lead, offer)
    except Exception as e:
        label, reasoning = mock_ai(lead, offer)
        reasoning = f"AI provider error: {e}. Fallback to mock."

    points = 50 if label=="High" else 30 if label=="Medium" else 10
    return label, reasoning, points

# -------------------------
# Quick demo
# -------------------------
if __name__ == "__main__":
    sample_offer = {
        "name": "AI Outreach Automation",
        "value_props": ["24/7 outreach", "6x more meetings"],
        "ideal_use_cases": ["B2B SaaS mid-market"]
    }
    sample_lead = {
        "name": "Ava Patel",
        "role": "Head of Growth",
        "company": "FlowMetrics",
        "industry": "SaaS",
        "location": "Bengaluru, India",
        "linkedin_bio": "Growth leader at FlowMetrics. Loves scaling SDR teams."
    }
    lbl, reason, pts = ai_classify(sample_lead, sample_offer)
    print("Label:", lbl)
    print("Reasoning:", reason)
    print("Points:", pts)
