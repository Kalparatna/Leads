from flask import Blueprint, request, jsonify, make_response
from services.ai import ai_classify
from services.rules import calculate_rule_score
from utils.storage import storage
import csv
import io

score_bp = Blueprint("score", __name__)

@score_bp.route("/score", methods=["POST"])
def score_leads():
    """Run scoring on uploaded leads using rule-based + AI scoring"""
    if not storage.get("offer"):
        return jsonify({"error": "No offer data found. Please upload offer first."}), 400
    
    if not storage.get("leads"):
        return jsonify({"error": "No leads data found. Please upload leads first."}), 400
    
    offer = storage["offer"]
    leads = storage["leads"]
    results = []
    
    for lead in leads:
        try:
            # Calculate rule-based score (max 50 points)
            rule_score = calculate_rule_score(lead, offer)
            
            # Get AI classification (max 50 points)
            ai_intent, ai_reasoning, ai_points = ai_classify(lead, offer)
            
            # Calculate final score
            final_score = rule_score + ai_points
            
            # Determine intent based on final score
            if final_score >= 70:
                intent = "High"
            elif final_score >= 40:
                intent = "Medium"
            else:
                intent = "Low"
            
            result = {
                "name": lead.get("name", ""),
                "role": lead.get("role", ""),
                "company": lead.get("company", ""),
                "intent": intent,
                "score": final_score,
                "reasoning": ai_reasoning
            }
            results.append(result)
            
        except Exception as e:
            # Handle individual lead scoring errors
            result = {
                "name": lead.get("name", ""),
                "role": lead.get("role", ""),
                "company": lead.get("company", ""),
                "intent": "Low",
                "score": 0,
                "reasoning": f"Error processing lead: {str(e)}"
            }
            results.append(result)
    
    # Store results for later retrieval
    storage["results"] = results
    
    return jsonify({
        "message": f"Scored {len(results)} leads successfully",
        "total_leads": len(results)
    }), 200

@score_bp.route("/results", methods=["GET"])
def get_results():
    """Return JSON array of scored leads"""
    if not storage.get("results"):
        return jsonify({"error": "No results found. Please run scoring first."}), 404
    
    return jsonify(storage["results"]), 200

@score_bp.route("/results/export", methods=["GET"])
def export_results_csv():
    """Export results as CSV file"""
    if not storage.get("results"):
        return jsonify({"error": "No results found. Please run scoring first."}), 404
    
    results = storage["results"]
    
    # Create CSV content
    output = io.StringIO()
    fieldnames = ["name", "role", "company", "intent", "score", "reasoning"]
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    
    writer.writeheader()
    for result in results:
        writer.writerow(result)
    
    # Create response
    csv_content = output.getvalue()
    output.close()
    
    response = make_response(csv_content)
    response.headers["Content-Disposition"] = "attachment; filename=lead_scores.csv"
    response.headers["Content-Type"] = "text/csv"
    
    return response

@score_bp.route("/classify", methods=["POST"])
def classify_lead():
    """Individual lead classification endpoint for testing"""
    data = request.get_json()
    if not data or "lead" not in data or "offer" not in data:
        return jsonify({"error": "Invalid input. 'lead' and 'offer' are required."}), 400

    lead = data["lead"]
    offer = data["offer"]

    ai_intent, ai_reason, ai_points = ai_classify(lead, offer)

    return jsonify({
        "intent": ai_intent,
        "reasoning": ai_reason,
        "points": ai_points
    }), 200