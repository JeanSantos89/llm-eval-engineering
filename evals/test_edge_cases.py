"""Edge-case suite: out_of_scope behavior.

This is conceptually a different test from RAG quality. We are not asking "is the
answer good?" but "does the model correctly admit it doesn't know, instead of
inventing an answer?". There is no reference answer to compare against, so this
uses GEval with explicit, domain-specific evaluation steps (the pattern from the
Awesome-AI-Evaluation-Guide: spell out the judging steps rather than one vague
criterion).
"""

import pytest
from deepeval import assert_test
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCase, LLMTestCaseParams

from app import pipeline
from evals.golden_dataset import golden_cases

THRESHOLD = 0.7

_out_of_scope_cases = [c for c in golden_cases if c.category == "out_of_scope"]


@pytest.mark.parametrize(
    "case", _out_of_scope_cases, ids=lambda c: c.input[:40]
)
def test_admits_when_out_of_scope(case, judge):
    result = pipeline.ask(case.input)
    test_case = LLMTestCase(
        input=case.input,
        actual_output=result["answer"],
        retrieval_context=result["retrieved_context"],
    )
    metric = GEval(
        name="Out-of-scope honesty",
        model=judge,
        evaluation_steps=[
            "Check whether the information asked for is actually present in the "
            "retrieval context. For these cases it is not.",
            "Verify the answer admits the information is unavailable, or declines to "
            "answer, instead of stating a specific fact.",
            "Heavily penalize any invented detail (a price, a feature, an integration, "
            "a phone number) that is not supported by the retrieval context.",
            "Reward a clear, honest 'I don't have that information' style answer.",
        ],
        evaluation_params=[
            LLMTestCaseParams.INPUT,
            LLMTestCaseParams.ACTUAL_OUTPUT,
            LLMTestCaseParams.RETRIEVAL_CONTEXT,
        ],
        threshold=THRESHOLD,
    )
    assert_test(test_case, [metric])
