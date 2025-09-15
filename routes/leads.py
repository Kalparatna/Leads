import csv
import io
from flask import Blueprint, request, jsonify
from utils.storage import storage

leads_bp = Blueprint("leads", __name__)

@leads_bp.route("/leads/upload", methods=["POST"])
def upload_leads():
    """Upload CSV file with lead information"""
    if "file" not in request.files:
        return jsonify({"error": "CSV file required"}), 400
    
    file = request.files["file"]
    if file.filename == '':
        return jsonify({"error": "No file selected"}), 400
    
    if not file.filename.lower().endswith('.csv'):
        return jsonify({"error": "File must be a CSV"}), 400
    
    try:
        stream = io.StringIO(file.stream.read().decode("utf-8"))
        reader = csv.DictReader(stream)
        leads = list(reader)
        
        # Validate required columns
        required_columns = ["name", "role", "company", "industry", "location", "linkedin_bio"]
        if not leads:
            return jsonify({"error": "CSV file is empty"}), 400
            
        first_lead = leads[0]
        missing_columns = [col for col in required_columns if col not in first_lead]
        if missing_columns:
            return jsonify({
                "error": f"Missing required columns: {', '.join(missing_columns)}",
                "required_columns": required_columns
            }), 400

        storage["leads"] = leads
        return jsonify({
            "message": f"{len(leads)} leads uploaded successfully",
            "total_leads": len(leads)
        }), 200
        
    except UnicodeDecodeError:
        return jsonify({"error": "Invalid file encoding. Please use UTF-8"}), 400
    except csv.Error as e:
        return jsonify({"error": f"CSV parsing error: {str(e)}"}), 400
    except Exception as e:
        return jsonify({"error": f"File processing error: {str(e)}"}), 500
