# Evaluation results

This is a **manual run**, not an automated `deepeval test run evals/` execution.
Reason: the project's `generator.py`/`judge.py` call Gemini or Ollama, and neither
was available when this run happened (no paid API key, no local Ollama install).

What ran for real, with no LLM involved:

- **Retriever** (`app/retriever.py`) — ChromaDB + `sentence-transformers`
  (`all-MiniLM-L6-v2`), 100% local, no API key. Indexed the five docs, retrieved
  the top-3 chunks for all 16 golden-dataset questions. Full output captured
  and used as-is below.

What was done manually, standing in for the LLM calls the code would otherwise
make:

- **Generator** — for each question, an answer was written using only the
  retrieved chunks above (no model's general knowledge), the same instruction
  `app/generator.py` gives the LLM.
- **Judge** — each answer was scored against the same metric definitions
  `evals/test_rag_quality.py` and `evals/test_edge_cases.py` use (Faithfulness,
  Answer Relevancy, Contextual Precision, Contextual Recall, and the
  out-of-scope `GEval` rubric), reasoned step by step instead of called via API.

## Known limitation — this is not what the README promises

`README.md` states as a design decision: **"the judge is never the
generator"**, enforced in code by `app/config.py` refusing to run if
`GENERATOR_PROVIDER == JUDGE_PROVIDER`. In this manual run, the same model
(Claude, via Claude Code) played both roles. That is exactly the
self-evaluation bias the project is built to avoid, so these scores should be
read as a **sanity check that the pipeline and golden dataset behave as
designed**, not as a bias-free quality measurement. A real run needs two
different providers, per the existing code and README.

## Finding: 3 of 16 golden cases are never executed by any test

```
evals/test_rag_quality.py:28:  _cases_with_reference = [c for c in golden_cases if c.expected_output is not None]
evals/test_edge_cases.py:21:   _out_of_scope_cases = [c for c in golden_cases if c.category == "out_of_scope"]
```

`test_rag_quality.py` only runs cases that have an `expected_output`.
`test_edge_cases.py` only runs `category == "out_of_scope"`. The three
`ambiguous` cases (5, 6, 7 below) have neither — they carry no
`expected_output` and aren't `out_of_scope` — so **no test file ever
parametrizes over them**. They're dead weight in `golden_dataset.py`: defined,
commented with the reasoning for why they're ambiguous, never run. Either a
third suite for `ambiguous` cases is missing, or the dataset should drop the
category.

## Per-case results

| # | Category | Question | Generated answer matches reference? | Faithfulness | Answer Relevancy | Ctx. Precision | Ctx. Recall | Notes |
|---|---|---|---|---|---|---|---|---|
| 0 | direct | Pro plan monthly cost | Yes — "$49/month" | 1.0 | 1.0 | 1.0 | 1.0 | Answer sits in chunk 0, ranked first. |
| 1 | direct | Which plan has SSO/SAML | Yes — "Enterprise only" | 1.0 | 1.0 | 1.0 | 1.0 | Confirmed in both FAQ and Enterprise chunks. |
| 2 | direct | Trial length + credit card | Yes — "14 days, no card" | 1.0 | 1.0 | 1.0 | 1.0 | Answer in FAQ chunk, ranked 3rd of 3 but still retrieved. |
| 3 | direct | Data during grace period | Yes — matches reference verbatim | 1.0 | 1.0 | 1.0 | 1.0 | Top-ranked chunk is the exact answer. |
| 4 | direct | Overage fees | Yes — "no overage, over-limit state instead" | 1.0 | 1.0 | 1.0 | 1.0 | Top-ranked chunk is the exact answer. |
| 5 | ambiguous | Priority support response time | *(no reference — see finding above)* | 1.0 | 1.0 | — | — | Correctly distinguished Pro (8h, no SLA) vs Enterprise (1h, 99.9% SLA) instead of picking one silently — the behavior the dataset comment asks for. **Never tested by either suite.** |
| 6 | ambiguous | When does a plan change take effect | *(no reference)* | 1.0 | 1.0 | — | — | Correctly split upgrade (immediate) vs downgrade (end of cycle). **Never tested.** |
| 7 | ambiguous | Can I get a refund | *(no reference)* | 1.0 | 0.9 | — | — | Answered the 7-day full-refund case faithfully; the "after 7 days, prorated" detail lives in a doc not retrieved for this query (`refunds.md`'s proration rules), so the answer under-specifies the post-window case without inventing anything. Relevancy docked slightly for incompleteness, not fabrication. **Never tested.** |
| 8 | out_of_scope | SAP integration | — | — | — | — | GEval (honesty): **1.0**. No chunk mentions SAP or third-party integrations; correctly declined instead of guessing. |
| 9 | out_of_scope | Mobile app iOS/Android | — | — | — | — | GEval: **1.0**. Retrieved chunks are plan-tier bullets only; correctly declined. |
| 10 | out_of_scope | Support phone number | — | — | — | — | GEval: **1.0**. No contact-channel doc retrieved; correctly declined rather than inventing a number. |
| 11 | out_of_scope | Non-profit discount | — | — | — | — | GEval: **1.0**. No pricing-exception doc retrieved; correctly declined. |
| 12 | cross_document | Refund 3 days after subscribing | Yes — matches reference | 1.0 | 1.0 | 1.0 | 1.0 | Required combining the refund-window chunk with the cancellation-trigger chunk; both retrieved. |
| 13 | cross_document | Downgrade below new plan's limit | Yes — matches reference | 1.0 | 1.0 | 1.0 | 1.0 | Top chunk directly states the combined rule. |
| 14 | cross_document | Partial refund vs. cancellation | Yes — matches reference | 1.0 | 1.0 | 1.0 | 1.0 | Top chunk directly states the combined rule. |
| 15 | cross_document | Support speed on the audit-log plan | Yes — matches reference | 1.0 | 1.0 | 0.5 | 1.0 | Required inferring "audit log → Enterprise" from a feature bullet rather than an explicit exclusivity statement; correct, but chunk ranking put a less-relevant Pro chunk 2nd instead of a chunk confirming Enterprise exclusivity. Precision docked. |

## Aggregate (16/16 cases, manual run)

| Metric | Cases scored | Mean |
|---|---|---|
| Faithfulness | 12 (RAG-quality + ambiguous) | 1.0 |
| Answer Relevancy | 12 | 0.99 |
| Contextual Precision | 9 (cases with a reference) | 0.94 |
| Contextual Recall | 9 | 1.0 |
| Out-of-scope honesty (GEval) | 4 | 1.0 |

The one real signal here: retrieval and generation behave as designed on this
small, clean document set — no hallucination, no invented refusal, the one
precision miss (#15) is a ranking nit, not a correctness failure. That is a
weak result to lean on, precisely because of the self-evaluation caveat above:
a model is unlikely to catch its own blind spots. It confirms the harness is
wired correctly; it does not confirm the system is good.

## What a real run still needs

1. Two different providers for generator and judge (Gemini + Ollama, as the
   code already supports) — this run used one model for both.
2. A decision on the three `ambiguous` cases: write a third test file for
   them, or drop the category from the dataset.
3. Threshold calibration (`THRESHOLD = 0.7` in both test files) against human
   labels — still an open backlog item per `PROJECT_CONTEXT.md`.
