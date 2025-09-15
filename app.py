from flask import Flask
from routes.offer import offer_bp
from routes.leads import leads_bp
from routes.score import score_bp

app = Flask(__name__)

# Register blueprints
app.register_blueprint(offer_bp, url_prefix="/")
app.register_blueprint(leads_bp, url_prefix="/")
app.register_blueprint(score_bp, url_prefix="/")

@app.route("/", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "message": "Lead Scoring API is running"}, 200

if __name__ == "__main__":
    app.run(debug=True, port=5000)
