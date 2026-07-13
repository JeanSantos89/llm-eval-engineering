"""Shared pytest fixtures for the eval suite."""

import pytest

from evals.judge import get_judge


@pytest.fixture(scope="session")
def judge():
    """The LLM judge, built once per test session."""
    return get_judge()
