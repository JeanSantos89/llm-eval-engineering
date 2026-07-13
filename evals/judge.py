"""Judge model for DeepEval metrics.

DeepEval defaults to OpenAI as the judge. This project forbids that (no OpenAI
dependency, and the judge must differ from the generator). This module returns a
judge model object built from JUDGE_PROVIDER, which config.py already guarantees
is different from the generator.
"""

from deepeval.models import GeminiModel, OllamaModel

from app import config


def get_judge():
    if config.JUDGE_PROVIDER == "ollama":
        return OllamaModel(model=config.OLLAMA_MODEL)
    if config.JUDGE_PROVIDER == "gemini":
        return GeminiModel(model_name=config.GEMINI_MODEL, api_key=config.GEMINI_API_KEY)
    raise ValueError(f"Unsupported JUDGE_PROVIDER: {config.JUDGE_PROVIDER}")
