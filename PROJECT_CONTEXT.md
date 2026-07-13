# Project Context

Handoff document. Read this at the start of any new session to resume without
re-explaining the project. Update it at the end of every meaningful session.

## What this is

An LLM evaluation lab (`nondeterministic-qa`) built around a small, realistic RAG
system for a fictional SaaS ("PlanFlow"). The product is invented; the evaluation
methodology is real. Portfolio piece: every decision is documented with its reasoning.

## Current phase

**Phase 1 — RAG quality.** The full Phase 1 code is written (app + golden dataset +
DeepEval suite) but has **never been run against a live provider**. Next milestone:
install dependencies, pick a provider, run `deepeval test run evals/`, fix what breaks,
record results.

## Architecture snapshot

```
docs/ → retriever → generator → pipeline.ask() → evals (DeepEval + golden dataset)
```

## Key decisions log

- 2026-07-13: Judge must differ from generator (self-bias); enforced in `config.py`.
- 2026-07-13: Generator/judge providers = Gemini free tier and/or Ollama local, chosen
  via env vars. No OpenAI dependency.
- 2026-07-13: Chunking = one chunk per markdown heading (each doc section is a
  self-contained rule).
- 2026-07-13: Embeddings = local all-MiniLM-L6-v2 (free, no key).
- 2026-07-13: Metric threshold = 0.7, uncalibrated placeholder; calibration is a
  Tier-1 backlog item.
- 2026-07-13: Golden dataset was AI-authored (docs + questions + expected answers all
  written by the assistant). Needs human curation to be portfolio-grade — the user
  should review each case and own it.

## What's implemented

- [x] `docs/` — 6 markdown files with deliberate ambiguities + cross-document links.
- [x] `app/config.py` — central config + generator≠judge guard.
- [x] `app/retriever.py` — heading chunking, sentence-transformers, ChromaDB, top-k.
- [x] `app/generator.py` — Gemini + Ollama providers, context-only system prompt.
- [x] `app/pipeline.py` — `ask()` returning `{answer, retrieved_context}`.
- [x] `evals/golden_dataset.py` — 16 cases across 4 categories.
- [x] `evals/judge.py` — judge model from JUDGE_PROVIDER (Ollama/Gemini).
- [x] `evals/conftest.py` — session-scoped judge fixture.
- [x] `evals/test_rag_quality.py` — 4 core metrics over cases with a reference answer.
- [x] `evals/test_edge_cases.py` — GEval for out_of_scope honesty.
- [x] README, .env.example, requirements.txt, .gitignore.

## What's NOT implemented yet

- [ ] Actually running the suite (deps not installed, no provider configured yet).
- [ ] Recording results in the README.
- [ ] Human curation of the golden dataset.
- [ ] `DEEPEVAL_METRICS_MATRIX.md` (spec asks for it as a living table).
- [ ] `pytest.ini`.
- [ ] CI (`.github/workflows/eval-ci.yml`).
- [ ] Phase 2+ (comparisons/, agent/, security/, observability/ placeholders).

## Known limitations / open questions

- Suite is unverified — first live run will likely surface bugs (provider SDK calls,
  DeepEval judge wiring).
- Local judge is noisier; 0.7 threshold is a guess, not calibrated.
- Golden dataset needs human review before it counts as portfolio evidence.

## Conventions in use

- Ponytail mode: **full** (repo code meant to last; simplest thing that works).
- Caveman mode: applies to work chat, not to docs/README. Safety warnings stay in
  full prose.
- Language: **all repo content in English**. Only the learning conversation with the
  user is in Portuguese.
