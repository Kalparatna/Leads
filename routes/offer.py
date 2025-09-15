from flask import Blueprint, request, jsonify
from utils.storage import storage

offer_bp = Blueprint("offer", __name__)

@offer_bp.route("/offer", methods=["POST"])
def create_offer():
    """Store product/offer information"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "JSON data required"}), 400
            
        # Validate required fields
        required_fields = ["name"]
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            return jsonify({
                "error": f"Missing required fields: {', '.join(missing_fields)}",
                "required_fields": required_fields
            }), 400
        
        # Validate optional fields have correct types
        if "value_props" in data and not isinstance(data["value_props"], list):
            return jsonify({"error": "value_props must be a list"}), 400
            
        if "ideal_use_cases" in data and not isinstance(data["ideal_use_cases"], list):
            return jsonify({"error": "ideal_use_cases must be a list"}), 400
        
        storage["offer"] = data
        return jsonify({
            "message": "Offer stored successfully", 
            "offer": data
        }), 200
        
    except Exception as e:
        return jsonify({"error": f"Server error: {str(e)}"}), 500
