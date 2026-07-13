"""Generator: ask the LLM to answer using ONLY the retrieved context.

The system prompt forces two behaviors we want to test later: answer strictly
from the given context, and admit when the answer is not there instead of making
something up. Supports two providers, chosen via GENERATOR_PROVIDER.
"""

from app import config

_SYSTEM_PROMPT = """You are a support assistant for a product called PlanFlow.
Answer the user's question using ONLY the context provided below.
If the answer is not in the context, say you don't have that information.
Do not invent details, prices, or policies that are not in the context."""


def _build_prompt(query: str, context: list[str]) -> str:
    joined = "\n\n---\n\n".join(context)
    return f"{_SYSTEM_PROMPT}\n\nContext:\n{joined}\n\nQuestion: {query}\n\nAnswer:"


def _generate_gemini(prompt: str) -> str:
    import google.generativeai as genai

    genai.configure(api_key=config.GEMINI_API_KEY)
    model = genai.GenerativeModel(config.GEMINI_MODEL)
    return model.generate_content(prompt).text.strip()


def _generate_ollama(prompt: str) -> str:
    import ollama

    response = ollama.generate(model=config.OLLAMA_MODEL, prompt=prompt)
    return response["response"].strip()


def generate(query: str, context: list[str]) -> str:
    """Answer a query grounded in the retrieved context."""
    prompt = _build_prompt(query, context)
    if config.GENERATOR_PROVIDER == "gemini":
        return _generate_gemini(prompt)
    if config.GENERATOR_PROVIDER == "ollama":
        return _generate_ollama(prompt)
    raise ValueError(f"Unknown GENERATOR_PROVIDER: {config.GENERATOR_PROVIDER}")
