import os
from groq import Groq


def call_llm_fast(prompt: str, max_tokens: int = 300, temperature: float = 0.1) -> str:
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY_1"))
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"}  # ← ADD THIS LINE
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise Exception(f"Groq account 1 failed: {e}")


def call_llm_quality(prompt: str, max_tokens: int = 500, temperature: float = 0.4) -> str:
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY_2"))
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
            # No response_format here - outreach is text, not JSON
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        raise Exception(f"Groq account 2 failed: {e}")