import os
from groq import Groq
import google.generativeai as genai

def call_llm(prompt: str, max_tokens: int = 500, temperature: float = 0.2) -> str:
    """Try Groq first, fall back to Gemini if rate limited."""
    # Try Groq
    try:
        client = Groq(api_key=os.getenv("GROQ_API_KEY"))
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=temperature,
            max_tokens=max_tokens
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        if "rate_limit" in str(e).lower() or "429" in str(e):
            print(f"[Groq rate limited] Falling back to Gemini...")
        else:
            print(f"[Groq error: {e}] Falling back to Gemini...")

    # Fallback to Gemini
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
    model = genai.GenerativeModel("gemini-1.5-flash-8b")
    response = model.generate_content(prompt)
    return response.text.strip()