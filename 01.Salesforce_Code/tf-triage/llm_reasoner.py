# llm_reasoner.py
import os
from typing import List
from openai import OpenAI

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
        e = m.get("entry", {})
        lines.append(
            f"- {e.get('id','?')}: {e.get('error_log','')}\n  resolution: {e.get('resolution','')}\n  similarity_score: {m.get('score',0):.4f}"
        )
    lines.append("\nAnswer in bullet points, short, technical.")
    return "\n".join(lines)

def get_recommendation(new_log, matches, model="gpt-4o-mini", max_tokens=500):
    endpoint = "https://enus2.openai.azure.com/openai/v1"
    deployment_name = "EnGPT-5"
    api_key = "B2s1q...3dQQ"

    client = OpenAI(
        base_url=endpoint,
        api_key=api_key
    )

    prompt = compose_prompt(new_log, matches)

    # Using Chat Completions style
    resp = client.chat.completions.create(
        model=deployment_name,
        messages=[{"role": "user", "content": prompt}]#,
        #max_tokens=max_tokens,
        #temperature=0.0
    )
    text = resp.choices[0].message.content.strip()
    return text
