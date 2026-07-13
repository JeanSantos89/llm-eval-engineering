"""RAG quality suite: the four core DeepEval metrics over the golden dataset.

Only cases that carry an expected_output run here, because two of the four
metrics (ContextualPrecision, ContextualRecall) need a reference answer. The
out_of_scope and ambiguous cases are tested separately in test_edge_cases.py.

Threshold = 0.7 for every metric: a starting point, not a calibrated value. A
local judge (Ollama) is noisier than a hosted one, so 0.7 leaves room for that
noise while still failing clearly bad answers. Calibrating this threshold against
human labels is a documented Tier-1 backlog item (Judge Calibration Report).
"""

import pytest
from deepeval import assert_test
from deepeval.metrics import (
    AnswerRelevancyMetric,
    ContextualPrecisionMetric,
    ContextualRecallMetric,
    FaithfulnessMetric,
)
from deepeval.test_case import LLMTestCase

from app import pipeline
from evals.golden_dataset import golden_cases

THRESHOLD = 0.7

_cases_with_reference = [c for c in golden_cases if c.expected_output is not None]


@pytest.mark.parametrize("case", _cases_with_reference, ids=lambda c: c.category + ": " + c.input[:40])
def test_rag_quality(case, judge):
    result = pipeline.ask(case.input)
    test_case = LLMTestCase(
        input=case.input,
        actual_output=result["answer"],
        retrieval_context=result["retrieved_context"],
        expected_output=case.expected_output,
    )
    metrics = [
        FaithfulnessMetric(threshold=THRESHOLD, model=judge),
        AnswerRelevancyMetric(threshold=THRESHOLD, model=judge),
        ContextualPrecisionMetric(threshold=THRESHOLD, model=judge),
        ContextualRecallMetric(threshold=THRESHOLD, model=judge),
    ]
    assert_test(test_case, metrics)
