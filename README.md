# FinGuru

A personal finance backend I am building step by step to learn backend and AI engineering.
Currently synthetic data only. Not financial advice.

## Status

**Built and tested (49 automated tests):**
- EMI, amortization schedule, loan affordability (40% EMI-to-income rule, an assumption)
- Monthly income/expense/savings summary
- SQLite storage (money stored as integer paise)
- Registration with Argon2 password hashing, JWT login, protected endpoints
- Per-user data isolation

**Planned (not built yet):**
- React dashboard, Financial Digital Twin, Next Best Action engine
- Fraud/anomaly detection, RAG knowledge assistant, LangGraph, MCP
- Rate limiting, deployment

## Run locally (Windows PowerShell)

```powershell
uv venv --python 3.11 .venv
.venv\Scripts\Activate.ps1
cd backend
uv pip install -r requirements.txt
Copy-Item .env.example .env
```

Put a random value for SECRET_KEY in `.env`. Generate one with:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Start the API, then open http://127.0.0.1:8000/docs :

```powershell
python -m uvicorn app.main:app --reload
```

## Run tests

```powershell
cd backend
python -m pytest -v
```

## Known limitations
- No rate limiting on login yet
- Dev database has no migrations
- Tokens are not revocable