# llm_reasoner.py
import os
import openai
import textwrap

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    print("Warning: OPENAI_API_KEY not set. LLM calls will fail unless set.")
openai.api_key = OPENAI_API_KEY

def compose_prompt(new_log, matches):
    lines = [
        "You are a helpful engineering triage assistant. A new test failure log is below. Use the historical matches to propose:",
        "1) A concise root-cause hypothesis",
        "2) A specific recommended fix (code/file/line suggestion if possible)",
        "3) A short confidence estimate (0-100)",
        "",
        "New Failure Log:",
        new_log,
        "",
        "Top similar historical failures (id, error_log, resolution):"
    ]
    for m in matches:
        e = m["entry"]
        lines.append(f"- {e.get('id','?')}: {e.get('error_log','')}\n  resolution: {e.get('resolution','')}\n  similarity_score: {m['score']:.4f}")
    lines.append("\nAnswer in bullet points, short, technical.")
    return "\n".join(lines)

def get_recommendation(new_log, matches, model="gpt-4o-mini", max_tokens=500):
    prompt = compose_prompt(new_log, matches)
    # Using Chat Completions style
    resp = openai.ChatCompletion.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        max_tokens=max_tokens,
        temperature=0.0
    )
    text = resp["choices"][0]["message"]["content"].strip()
    return text
