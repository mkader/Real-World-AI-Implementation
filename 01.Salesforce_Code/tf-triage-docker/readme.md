* TF Triage Agent into a deployable dev stack using Docker + docker-compose with:
    - FastAPI web app (triage API)
    - RQ + Redis queue for async, decoupled processing
    - Postgres for persistence (replacing SQLite)
    - FAISS index persisted in a Docker volume
    - Single reusable image used for both web and worker (small entrypoint switch)
    - Environment variables via .env
* Updated Python snippets (storage, triage_api, worker) that wire PostgreSQL + Redis.
* Everything is ready to run with ```docker compose up --build```.

* Project structure
    1. Dockerfile
    2. docker-compose.yml
    3. requirements.txt (updated)
    4. .env.example (copy to .env and edit)
    5. Updated storage.py (Postgres via SQLAlchemy)
    6. Updated triage_api.py (enqueue to RQ)
        - Note: queue.enqueue("worker.process_failure", ...) references the process_failure function in worker.py. RQ imports the module by name.
    7. worker.py (RQ worker tasks + triage logic)
    8. retriever.py (adjusted to read env paths)
    9.  build_index.py (ensure it writes into /app/index_data)
    10. llm_reasoner.py (unchanged, but reads OPENAI_API_KEY env var)

### Quick start (how to run)
  * Copy .env.example to .env and set OPENAI_API_KEY (if you want real LLM calls).
  * Build the FAISS index locally or rely on container building:
      - Option A (recommended before ```docker compose up```): run locally to populate indexdata volume path ./index_data: ```python build_index.py```
          - This writes tf_index.faiss and tf_meta.json into index_data (the compose volume mounts it).
      - Option B: let web service build the index on first run (not automated in compose; you can exec into container and run ```python build_index.py```).
  * Start the stack: ```docker compose up --build```
  * Submit a failure:
    ```
    curl -X POST "http://localhost:8000/submit_failure" \
      -H "Content-Type: application/json" \
      -d '{"error_log":"NullPointerException at PaymentService.validate() when processing order batch."}'
    ```
  * Watch logs:
    - web container will accept requests and enqueue jobs
    - worker container prints triage results when its RQ worker runs and persists them into Postgres
  * Inspect persisted results in Postgres (e.g., psql into container or use any PG client) — table triage_results.

### Notes, tradeoffs and extras
  * I used RQ because it's lightweight and ideal for dev stacks. For production consider Celery, Prefect, or a managed queue.
  * The image currently runs build_index.py manually — for heavy embedding downloads you may prefer to prebuild the index and mount it into the container/volume instead of building in image build.
  * FAISS is CPU-based here (faiss-cpu). For large-scale production consider vector DBs (Milvus, Qdrant, Pinecone) and GPU FAISS builds.
  * The LLM calls use openai.ChatCompletion — ensure you have API key or replace with your internal model endpoint.
