# Smart Scheduling Agent

This standalone microservice schedules appointments and prevents double-booking. It uses a local SQLite database (`scheduling-agent.db`) to track real bookings across multiple requests and injects this context into the LLM prompt so Gemini can intelligently detect conflicts and suggest alternatives.

## Running Locally

1. Set your Gemini API key in `.env`
2. Run `pip install -r requirements.txt`
3. Start the server: `uvicorn app.main:app --port 8003 --reload`

## Example Request (First Booking)

```bash
curl -X POST http://127.0.0.1:8003/schedule \
-H "Content-Type: application/json" \
-d '{
  "patient_name": "Alice",
  "doctor_name": "Dr. Smith",
  "preferred_date": "2026-07-30",
  "preferred_time": "10:00"
}'
```
