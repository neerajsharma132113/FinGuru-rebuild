# FinGuru architecture

## 1. System overview

```mermaid
flowchart LR
  U["Browser: React + Vite"] -->|"JSON + JWT"| API["FastAPI"]
  API --> FIN["finance.py<br/>EMI, schedule, twin, next action, health check"]
  API --> FR["fraud.py<br/>risk score"]
  API --> RAG["rag.py<br/>TF-IDF search over notes"]
  API --> DB["SQLite<br/>users, transactions"]
  FR --> M["fraud_model.joblib"]
  RAG --> N["knowledge notes (markdown)"]
  WF["workflow.py<br/>LangGraph health check"] --> FIN
  MCP["MCP server<br/>stdio, read-only tools"] --> FIN
```

The API and the MCP tools only validate inputs and call the same tested functions. The MCP server never touches the database.

## 2. Risk check: training happens offline, scoring happens online

```mermaid
flowchart TB
  subgraph Offline["Offline (run once)"]
    G["ml/generate_data.py<br/>synthetic transactions"] --> T["ml/train_final.py<br/>train, tune threshold on a validation set"]
    T --> F["backend/models/fraud_model.joblib"]
  end
  subgraph Online["Online (every request)"]
    R["GET /fraud-score (login required)"] --> L["model loaded once at startup"]
    L --> S["score, threshold, main factors"]
    S --> O["flag for review, never blocks"]
  end
  F --> L
```

## 3. Health check workflow (LangGraph)

```mermaid
flowchart LR
  A["summarize_step"] -->|"no transactions"| B["no_data_step"] --> E(("END"))
  A -->|"latest month has no income"| C["no_income_step"] --> E
  A -->|"otherwise"| D["trend_step"] --> F["advice_step"] --> G["finish_step"] --> E
```

A test checks that this graph and the plain `health_check` function return identical results for six cases.

## 4. Design decisions

- **Arithmetic lives in plain, tested functions.** The API, the graph and the MCP tools wrap them and add no logic.
- **No LLM in the app.** Numbers and suggestions come from rules and a small model. The chat answers only from retrieved notes and says so when it finds nothing.
- **Every private query filters by the user id from the token.** Ownership is checked in the SQL itself.
- **Limits at two layers.** The API rejects out-of-range numbers, and the service functions check again, so other callers are protected too.
- **Honest scope.** The risk model is trained on synthetic data, the notes are three short files, and login limits are in memory. See the README's known limitations.