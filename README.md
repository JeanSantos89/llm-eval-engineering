# nondeterministic-qa

An evaluation lab for a small but realistic RAG system. It exists to practice and
demonstrate the discipline of **LLM evaluation** — measuring the quality of a
non-deterministic, LLM-based system with the same rigor a QA engineer brings to
deterministic software.

**→ See [RESULTS.md](./RESULTS.md) for an actual run of this pipeline**, including
a real bug found in the test suite and an explicit caveat about the conditions
under which it ran.

## Why this exists

Traditional test automation asserts exact outputs: a value either equals the
expected one or it doesn't. LLM systems break that model — the same question can be
answered correctly in many different wordings, so `assert actual == expected` no
longer applies. This project is a hands-on study of what replaces it: scored
metrics, an LLM-as-judge, retrieval-quality measurement, and hallucination
detection. It is built as a portfolio piece: every technical decision is documented
with its reasoning, not just implemented.

The product it evaluates ("PlanFlow", a fictional subscription-management SaaS) is
invented. The evaluation methodology around it is real.

## Architecture

```
docs/  →  retriever  →  generator  →  pipeline  →  evals
(source    (embed +     (LLM answers   (ask() ties   (DeepEval
 of truth)  ChromaDB      from context)  it together)  metrics +
            search)                                    golden dataset)
```

- **docs/** — the product knowledge base. Written with deliberate ambiguities and
  cross-document dependencies so the evals test real failure modes, not a happy path.
- **app/retriever.py** — chunks the docs by heading, embeds them with
  sentence-transformers, indexes them in ChromaDB, and returns the top-k chunks for a
  query by vector similarity.
- **app/generator.py** — prompts the LLM to answer using only the retrieved context
  and to admit when it doesn't know, instead of inventing an answer.
- **app/pipeline.py** — exposes `ask(question)` returning `{answer, retrieved_context}`,
  the exact shape a DeepEval `LLMTestCase` consumes.
- **evals/** — the golden dataset plus the DeepEval suite that scores the system.

## Key decisions and trade-offs

- **Gemini / Ollama, not OpenAI.** Both the generator and judge run on a free tier
  (Gemini) or fully local (Ollama), so the lab has no hard dependency on a paid API.
- **The judge is never the generator.** The model that answers is never the model
  that scores, to avoid the known self-evaluation bias where a model rewards answers
  in its own style. `app/config.py` enforces this and refuses to run if they match.
- **ChromaDB as the vector store.** It runs from a local file with no external
  infrastructure — the right amount of realism for a lab without operational overhead.
- **Local embeddings (all-MiniLM-L6-v2).** Free, no rate limits, no API key.
- **Known limitation — judge noise.** A local judge (Ollama) produces noisier scores
  than a hosted one. Metric thresholds start at 0.7 and are not yet calibrated;
  calibrating them against human labels is a planned backlog item.

## The evaluation

A golden dataset of categorized questions drives the suite. Each category targets a
different failure mode:

| Category | What it tests |
|---|---|
| `direct` | a clear answer sits in one document |
| `ambiguous` | more than one reasonable interpretation |
| `out_of_scope` | the answer is not in the docs — the model must admit it, not invent |
| `cross_document` | the answer requires combining two documents |

Metrics (DeepEval):

| Metric | What it validates | Needs a reference answer? |
|---|---|---|
| Faithfulness | Did the answer invent anything absent from the retrieved context? | No |
| Answer Relevancy | Is the answer on-topic for the question? | No |
| Contextual Precision | Were the relevant chunks ranked first? | Yes |
| Contextual Recall | Did retrieval bring back everything needed? | Yes |

Out-of-scope cases use a `GEval` metric with explicit, domain-specific judging steps,
since the goal there is honest refusal, not answer quality.

## Running locally

```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                 # then fill in your provider
deepeval test run evals/
```

You need one generator provider (a `GEMINI_API_KEY`, or Ollama running locally) and a
different judge provider. See `.env.example`.

## Roadmap

- **Phase 1 — RAG quality (in progress):** DeepEval suite over the golden dataset.
- **Phase 2 — Framework comparison:** run the same dataset through RAGAS and compare.
- **Phase 2.5 — Agentic evaluation:** evolve the RAG into a LangGraph agent with a
  tool, validated with deterministic Tool Correctness.
- **Phase 3 — Security / red teaming:** prompt injection, jailbreak, prompt/context
  extraction (Garak, DeepTeam, Promptfoo, PyRIT).
- **Phase 4 — Continuous observability:** Langfuse tracing with referenceless metrics
  over simulated production traffic.

## Results

Not yet recorded — the suite has been written but not yet run against a live provider.
This section will hold per-category scores once the first run completes.
