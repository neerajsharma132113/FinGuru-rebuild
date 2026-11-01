# FinGuru

A personal finance app I am building step by step to learn backend, frontend, applied ML, retrieval and agent workflows.
It uses synthetic data only. Nothing here is financial advice.

## What it does

- **Finance engine:** EMI, amortization schedule, loan affordability, monthly income/expense/savings summary
- **Digital Twin:** what-if scenarios (income change, new loan) with before/after comparison
- **Next Best Action:** readable rules (HELP, WARN, SAVE, NO ACTION), each result includes the reason and the numbers behind it
- **Health check:** a workflow that summarizes the latest month, the savings trend and the next action. Built twice: as a plain function and as a LangGraph graph; a test checks both give identical results
- **Fraud check:** a model trained on synthetic data scores a transaction and lists the main factors. It flags for review and never blocks anything
- **Ask (retrieval chat):** answers only from three short notes written for this project, shows the source passages, and says "not found" instead of guessing. There is no LLM in this app
- **MCP server:** three read-only tools (EMI calculator, next action, loan comparison) that wrap the same tested functions

## Architecture

```
React (Vite) --HTTP+JWT--> FastAPI --> service functions (finance.py, fraud.py, rag.py, workflow.py)
                                   --> SQLite (users, transactions)
MCP server (stdio) -----------------> the same service functions (no database access)
```

Rules I followed: all arithmetic lives in plain, tested Python functions; the API and MCP tools only validate inputs and call them.
Detailed diagrams (system overview, risk-check flow, LangGraph workflow): [docs/architecture.md](docs/architecture.md)
## Security

- Argon2 password hashing, JWT access tokens (30 minutes), per-user data isolation (every query filters by the user id from the token)
- Login rate limiting: 5 failed attempts lock an email for 15 minutes
- Input limits on every endpoint, and again inside the service functions, so MCP and the graph are protected too
- CORS allows only the local frontend
- Hostile-input tests: SQL injection text, oversized fields, forged and unsigned tokens, `inf`/`nan`/huge numbers. Writing them found 9 real failures (crashes and unbounded values), which were then fixed
- The MCP tools are read-only and never touch the database

## Fraud model results (synthetic data)

Data: 10,000 generated transactions, 2% fraud, fixed seed. Test set: 2,000 rows with 40 fraud cases.

| Approach | Precision | Recall | PR-AUC |
|---|---|---|---|
| Rule: amount above 3000 | 0.185 | 0.375 | 0.319 |
| Isolation Forest (never sees labels) | 0.698 | 0.75 | 0.794 |
| Logistic Regression, threshold 0.5 | 0.293 | 0.90 | 0.862 |
| Logistic Regression, threshold 0.95 (chosen on a validation set) | 0.78 | 0.80 | n/a |

How to read this:
- I generated the data, so the fraud patterns are my own assumptions. These numbers show the workflow, not real-world accuracy.
- With 40 fraud cases in the test set, one case moves recall by 2.5 points.
- The threshold was chosen on 32 validation fraud cases and was the last value in my search grid.
- Isolation Forest was told the true fraud rate (`contamination=0.02`), which would be unknown in real life.
- The tuned row comes from a separate run that trains on a smaller training set (a validation set was held out), so its 0.5-threshold precision is 0.308 and not 0.293.

## Retrieval results (3 short notes)

TF-IDF keyword search, evaluated on questions I wrote (18 tuning, 8 held-out):

| Setup | Answered correctly | Correctly returned nothing |
|---|---|---|
| Score cut-off only (tuning set) | 13/14 | 0/4 |
| Plus coverage guard 0.5 (tuning set) | 11/14 | 4/4 |
| Coverage guard 0.5 (held-out set) | 4/5 | 3/3 |

How to read this:
- Out-of-scope questions ("which mutual fund should I buy?") matched on a single shared word. The coverage guard fixes that, at the cost of 2 more missed real questions.
- The question sets are tiny and written by me, so treat these as rough signals.
- Keyword search cannot match paraphrases. Embeddings would help but were not built.
- The three notes are written for this project and do not cover regulations, tax or investments.

## Run locally (Windows PowerShell)

Backend:

```powershell
uv venv --python 3.11 .venv
.venv\Scripts\Activate.ps1
cd backend
uv pip install -r requirements.txt
Copy-Item .env.example .env
```

Put a long random value in `.env` as `SECRET_KEY`. Generate one with:

```powershell
python -c "import secrets; print(secrets.token_hex(32))"
```

Create the fraud model (from the project root):

```powershell
uv pip install -r ml\requirements.txt
python ml\generate_data.py
python ml\train_final.py
```

Start the API (from `backend`), then open http://127.0.0.1:8000/docs :

```powershell
python -m uvicorn app.main:app --reload
```

Frontend (second window):

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

MCP server (from `backend`, normally launched by an MCP client):

```powershell
python mcp_server.py
python try_client.py
```

## Run tests

```powershell
cd backend
python -m pytest -q
```

## Known limitations

- Login rate limiting is in memory: it resets on restart and is per email only (no IP limit)
- The access token lives in memory, so refreshing the page logs you out; tokens cannot be revoked
- The dev database has no migrations
- The fraud model is trained on synthetic data and has not been tested on real transactions
- Next Best Action thresholds (40% EMI share, 3-month emergency fund) are assumptions, not professional advice
- The Ask chat answers each question on its own (no memory of earlier messages)

## Planned, not built

- An LLM-written answer in the chat (skipped on purpose to keep the app deterministic)
- Embedding-based retrieval, loading states in the UI
- Docker, deployment, end-to-end tests