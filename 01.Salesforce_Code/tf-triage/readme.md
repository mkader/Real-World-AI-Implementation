* Ready-to-run Python reference implementation of a TF Triage Agent inspired by the Salesforce design. It includes:
  - embeddings (sentence-transformers)
  - FAISS index building + querying
  - lightweight LLM reasoning wrapper (OpenAI example)
  - async, decoupled triage worker (FastAPI + in-process queue for simplicity)
  - persistence hook (SQLite example)
  - sample data and run instructions
    
* repo layout
```
tf-triage/
├─ requirements.txt
├─ sample_data/
│  └─ historical_failures.json
├─ build_index.py
├─ retriever.py
├─ llm_reasoner.py
├─ storage.py
├─ triage_api.py
├─ run_demo.sh
└─ README.md
```
* requirements.txt
  - install with ```pip install -r requirements.txt```
* sample_data/historical_failures.json
* build_index.py
  - Build embeddings for historical failures and write FAISS index + metadata file.
  - Run ```python build_index.py```
* retriever.py
  - Encapsulates loading the FAISS index, encoding queries, and returning nearest historical matches.
* llm_reasoner.py
  - Small wrapper to call an LLM on the retrieved context and produce a clear recommendation.
  - Example uses openai — set OPENAI_API_KEY env var.
  - If you use another LLM provider, replace this function.
  - ```Note: adjust model to your available model. Keep temperature=0.0 for deterministic/precise suggestions.```
* storage.py
  - Simple SQLite persistence for triage results (easy to swap with MySQL/Postgres later).
  - Call init_db() once at startup.
* triage_api.py
  - FastAPI app that accepts failures, queues them for asynchronous triage, and returns immediately (non-blocking).
  - Worker uses retriever + llm_reasoner + storage.
  - Run ```uvicorn triage_api:app --reload --port 8000```
  - Then
    ```
    POST http://localhost:8000/submit_failure
    Body: {"error_log": "NullPointerException at PaymentService.validate() when processing order batch..."}
    ```
  - Response returns immediately; triage worker prints & persists the recommendation.
  - <img width="878" height="441" alt="image" src="https://github.com/user-attachments/assets/da95176f-f87a-49c7-a74e-a88fedc0b27c" />
  - <img width="1752" height="447" alt="image" src="https://github.com/user-attachments/assets/39e35893-d26e-412c-a6f4-963722072120" />

* run_demo.sh
  - Example script to build index and start the API:
    ```
    #!/usr/bin/env bash
    set -e
    python build_index.py
    export OPENAI_API_KEY="sk-..."   # set properly or use local LLM wrapper
    uvicorn triage_api:app --reload --port 8000
    ```
### Quick demo flow
1. populate sample_data/historical_failures.json (or point to your historical store)
1. python build_index.py
1. set OPENAI_API_KEY (or adapt llm_reasoner.py to your LLM)
1. uvicorn triage_api:app --reload --port 8000
1. POST failure logs to /submit_failure and watch worker print/save recommendations.
