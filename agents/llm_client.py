import os
from groq import Groq


def call_llm_fast(prompt: str, max_tokens: int = 300, temperature: float = 0.1) -> str:
    """Extraction tasks — Groq Account 1."""
    client = Groq(api_key=os.getenv("GROQ_API_KEY_1"))
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content.strip()


def call_llm_quality(prompt: str, max_tokens: int = 500, temperature: float = 0.4) -> str:
    """Writing tasks — Groq Account 2, separate daily limit."""
    client = Groq(api_key=os.getenv("GROQ_API_KEY_2"))
    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens
    )
    return response.choices[0].message.content.strip()