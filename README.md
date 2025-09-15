# Lead Scoring API

A backend service that accepts product/offer information and CSV files of leads, then scores each lead's buying intent using rule-based logic combined with AI reasoning.

## Features

- **Product/Offer Management**: Store product details and value propositions
- **Lead Upload**: Bulk upload leads via CSV files
- **Intelligent Scoring**: Hybrid scoring system combining rule-based logic (max 50 points) and AI classification (max 50 points)
- **Intent Classification**: Automatically categorizes leads as High/Medium/Low intent
- **Results Export**: Export scored results as JSON or CSV

## API Endpoints

### 1. POST /offer
Accept JSON with product/offer details.

**Request Body:**
```json
{
  "name": "AI Outreach Automation",
  "value_props": ["24/7 outreach", "6x more meetings"],
  "ideal_use_cases": ["B2B SaaS mid-market"]
}
```

**cURL Example:**
```bash
curl -X POST http://localhost:5000/offer \
  -H "Content-Type: application/json" \
  -d '{
    "name": "AI Outreach Automation",
    "value_props": ["24/7 outreach", "6x more meetings"],
    "ideal_use_cases": ["B2B SaaS mid-market"]
  }'
```

### 2. POST /leads/upload
Accept a CSV file with lead information.

**Required CSV Columns:**
- name
- role
- company
- industry
- location
- linkedin_bio

**cURL Example:**
```bash
curl -X POST http://localhost:5000/leads/upload \
  -F "file=@leads.csv"
```

### 3. POST /score
Run scoring on uploaded leads.

**cURL Example:**
```bash
curl -X POST http://localhost:5000/score
```

### 4. GET /results
Return JSON array of scored leads.

**Response Format:**
```json
[
  {
    "name": "Ava Patel",
    "role": "Head of Growth",
    "company": "FlowMetrics",
    "intent": "High",
    "score": 85,
    "reasoning": "Decision-maker at an organization matching ICP (SaaS/software)."
  }
]
```

**cURL Example:**
```bash
curl -X GET http://localhost:5000/results
```

### 5. GET /results/export
Export results as CSV file.

**cURL Example:**
```bash
curl -X GET http://localhost:5000/results/export -o lead_scores.csv
```

## Scoring Logic

### Rule Layer (Max 50 Points)

1. **Role Relevance (0-20 points)**
   - Decision maker roles (Head, Chief, Director): +20 points
   - Influencer roles (Manager, Lead): +10 points
   - Other roles: 0 points

2. **Industry Match (0-20 points)**
   - Exact ICP match: +20 points
   - Adjacent industry (tech, software, B2B): +10 points
   - Other industries: 0 points

3. **Data Completeness (0-10 points)**
   - All required fields present: +10 points
   - Missing fields: 0 points

### AI Layer (Max 50 Points)

The AI analyzes the lead profile against the offer context and provides:
- **High Intent**: 50 points
- **Medium Intent**: 30 points
- **Low Intent**: 10 points

**AI Prompt Used:**
```
Offer: [offer details]
Lead: [lead details]

Task: Classify buying intent as High/Medium/Low and provide 1-2 sentence reasoning.
Respond in 1 line with the label first followed by reasoning.
```

### Final Scoring

- **Final Score** = Rule Score + AI Points (0-100)
- **Intent Classification**:
  - High: 70+ points
  - Medium: 40-69 points
  - Low: 0-39 points

## Setup Instructions

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Clone the repository:**
```bash
git clone <repository-url>
cd lead-scoring-api
```

2. **Create virtual environment:**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables:**
Create a `.env` file in the root directory:
```env
AI_PROVIDER=vertex_api_key
PROJECT_ID=your-google-project-id
VERTEX_API_KEY=your-vertex-api-key
MODEL=publishers/google/models/gemini-2.0-flash
GEMINI_API_KEY=your-gemini-api-key
```

5. **Run the application:**
```bash
python app.py
```

The API will be available at `http://localhost:5000`

## Sample CSV Format

Create a `leads.csv` file with the following format:

```csv
name,role,company,industry,location,linkedin_bio
Ava Patel,Head of Growth,FlowMetrics,SaaS,Bengaluru India,Growth leader at FlowMetrics. Loves scaling SDR teams.
John Smith,Software Engineer,TechCorp,Technology,San Francisco USA,Full-stack developer with 5 years experience.
Sarah Johnson,Marketing Manager,RetailCo,Retail,New York USA,Digital marketing specialist focused on e-commerce.
```

## Testing the Complete Flow

1. **Upload an offer:**
```bash
curl -X POST http://localhost:5000/offer \
  -H "Content-Type: application/json" \
  -d '{
    "name": "AI Outreach Automation",
    "value_props": ["24/7 outreach", "6x more meetings"],
    "ideal_use_cases": ["B2B SaaS mid-market"]
  }'
```

2. **Upload leads:**
```bash
curl -X POST http://localhost:5000/leads/upload \
  -F "file=@leads.csv"
```

3. **Run scoring:**
```bash
curl -X POST http://localhost:5000/score
```

4. **Get results:**
```bash
curl -X GET http://localhost:5000/results
```

5. **Export as CSV:**
```bash
curl -X GET http://localhost:5000/results/export -o scored_leads.csv
```

## Project Structure

```
backend/
├── app.py              # Flask entry point
├── routes/
│   ├── offer.py        # POST /offer
│   ├── leads.py        # POST /leads/upload
│   └── score.py        # POST /score, GET /results
├── services/
│   ├── rules.py        # Rule-based scoring logic
│   └── ai.py           # AI reasoning (Gemini integration)
├── utils/
│   └── storage.py      # In-memory storage
├── requirements.txt    # Dependencies
├── .env               # Environment variables
└── README.md          # This file
```

## AI Integration

The service integrates with Google's Gemini AI model through Vertex AI. The AI provider can be configured via environment variables:

- `AI_PROVIDER`: Set to "vertex_api_key" for Gemini or "mock" for testing
- `VERTEX_API_KEY`: Your Vertex AI API key
- `PROJECT_ID`: Your Google Cloud project ID
- `MODEL`: The Gemini model to use

## Error Handling

The API includes comprehensive error handling:
- Invalid JSON requests return 400 status codes
- Missing required data returns appropriate error messages
- AI service failures fall back to mock classification
- Individual lead processing errors are handled gracefully

## Deployment

The service is designed to be easily deployable on platforms like:
- Render
- Railway
- Vercel
- Heroku
- Google Cloud Run

For deployment, ensure all environment variables are properly configured in your hosting platform.

## Development

### Running in Development Mode
```bash
python app.py
```

The application runs with debug mode enabled on port 5000.

### Running Tests

**Unit Tests for Rule Layer:**
```bash
python test_rules.py
```

**API Integration Tests:**
```bash
python test_api.py
```

### Adding New Features
- Add new routes in the `routes/` directory
- Implement business logic in `services/`
- Use `utils/storage.py` for data persistence (consider upgrading to a database for production)

### Docker Deployment

**Build the Docker image:**
```bash
docker build -t lead-scoring-api .
```

**Run the container:**
```bash
docker run -p 5000:5000 --env-file .env lead-scoring-api
```

## License

This project is created for the Backend Engineer Hiring Assignment.