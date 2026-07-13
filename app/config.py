"""Central configuration for the PlanFlow RAG lab.

All environment reads live here so tests and app code never touch os.environ
directly. See .env.example for the variables and README for the reasoning behind
keeping the generator and judge models separate.
"""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Paths
ROOT = Path(__file__).resolve().parent.parent
DOCS_DIR = ROOT / "docs"
CHROMA_DIR = ROOT / ".chroma"

# Embedding model (local, free, no API key)
EMBEDDING_MODEL = "all-MiniLM-L6-v2"

# Generator: the model that answers the customer.
GENERATOR_PROVIDER = os.getenv("GENERATOR_PROVIDER", "gemini")  # "gemini" | "ollama"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")

# Judge: the model that scores DeepEval metrics. Must differ from the generator
# to avoid self-evaluation bias.
JUDGE_PROVIDER = os.getenv("JUDGE_PROVIDER", "ollama")  # "ollama" | "gemini" | "groq"

if GENERATOR_PROVIDER == JUDGE_PROVIDER:
    raise ValueError(
        f"Generator and judge must differ (both are '{GENERATOR_PROVIDER}'). "
        "This project forbids self-evaluation; see README."
    )
