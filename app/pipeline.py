"""Pipeline: the single entry point that wires retrieval + generation together.

ask() returns exactly the two fields DeepEval's LLMTestCase needs:
  - answer            -> actual_output
  - retrieved_context -> retrieval_context
"""

from app import generator, retriever


def ask(question: str, k: int = 3) -> dict:
    context = retriever.retrieve(question, k=k)
    answer = generator.generate(question, context)
    return {"answer": answer, "retrieved_context": context}
