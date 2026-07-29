# Medication Safety Agent

This agent checks a list of medications for potential drug-drug interactions.
It relies purely on the LLM's own clinical knowledge and does not require a local ChromaDB instance, as the original `medication_safety.py` implementation natively performed all checks via Gemini prompts without RAG.

## Running Locally

1. Set your Gemini API key in `.env`
2. Run `pip install -r requirements.txt`
3. Start the server: `uvicorn app.main:app --port 8002 --reload`

## Example Request (Interaction Case)

```bash
curl -X POST http://127.0.0.1:8002/check-interactions \
-H "Content-Type: application/json" \
-d '{
  "medications": ["Warfarin", "Ibuprofen"],
  "patient_age": 65
}'
```
