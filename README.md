# Intelligent Bank FAQ Agent

Production-ready conversational banking FAQ agent using **Python + LangChain + FastAPI + Gemini API**.

## Features
- Conversational LangChain agent with session memory.
- Custom tools:
  - Knowledge base retriever
  - FAQ lookup
  - Banking calculator
- FastAPI backend endpoint for real-time customer interaction.
- Prompt engineering + response guardrails for safe, grounded financial responses.

## Project Structure
```text
Intelligent_Bank_FAQ/
├─ app/
│  ├─ main.py
│  ├─ config.py
│  ├─ schemas.py
│  └─ agents/
│     ├─ bank_agent.py
│     ├─ prompts.py
│     └─ tools.py
├─ frontend/
│  ├─ src/
│  │  ├─ App.jsx
│  │  ├─ main.jsx
│  │  └─ index.css
│  ├─ package.json
│  └─ .env.example
├─ data/
│  ├─ faqs.json
│  └─ knowledge_base.md
├─ .env.example
└─ requirements.txt
```

## Setup
1. Create and activate a virtual environment.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Copy env file and set your Gemini key:
   ```bash
   copy .env.example .env
   ```
4. Update `.env` with:
   - `GOOGLE_API_KEY`
   - optional `GEMINI_MODEL`

## Run API
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Run React Frontend
1. Open a new terminal and move to frontend:
  ```bash
  cd frontend
  ```
2. Install Node dependencies:
  ```bash
  npm install
  ```
3. Create frontend env file:
  ```bash
  copy .env.example .env
  ```
4. Start React dev server:
  ```bash
  npm run dev
  ```
5. Open:
  - `http://localhost:5173`

By default, frontend calls backend at `http://127.0.0.1:8000`.

## API Usage
### Health check
`GET /health`

### Ask question
`POST /ask`

Request body:
```json
{
  "session_id": "cust-123",
  "question": "How is EMI calculated for a 5 lakh loan?"
}
```

Sample response:
```json
{
  "answer": "EMI depends on principal, tenure, and interest rate...",
  "model": "gemini-1.5-flash",
  "session_id": "cust-123"
}
```

## Notes
- This implementation provides customer-support style guidance, not legal or investment advice.
- Final eligibility, rates, and charges must be confirmed from official bank/NBFC policy.
