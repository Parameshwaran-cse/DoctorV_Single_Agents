# Patient Intake Agent

This standalone microservice acts as the Patient Intake Agent. It receives raw patient data and uses Google Gemini to generate a consultation-ready structured summary, including a triage priority and intelligent follow-up questions.

## Running Locally

1. Create a `.env` file and set your Gemini API key:
   ```
   GEMINI_API_KEY=your_key_here
   GEMINI_MODEL=gemini-2.5-flash
   ```
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Run the FastAPI server:
   ```
   uvicorn app.main:app --port 8001 --reload
   ```

## Example Request

```bash
curl -X POST http://127.0.0.1:8001/intake \
-H "Content-Type: application/json" \
-d '{
  "first_name": "Jane",
  "last_name": "Smith",
  "date_of_birth": "1985-04-12",
  "gender": "female",
  "chief_complaint": "Severe abdominal pain for 3 hours",
  "symptoms": ["abdominal pain", "nausea"],
  "symptom_severity": 8,
  "vital_signs": {
    "heart_rate": "110 bpm"
  }
}'
```
