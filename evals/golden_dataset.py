"""Golden dataset for the PlanFlow RAG evals.

Each case carries an explicit category, because different categories test
different failure modes (see README / DEEPEVAL_METRICS_MATRIX):

  - direct         : answer sits plainly in one document
  - ambiguous      : more than one reasonable interpretation
  - out_of_scope   : the answer is NOT in the docs; the model must admit it
  - cross_document : answer requires combining two documents

expected_output is only filled where a reference answer is meaningful. Context
metrics (ContextualPrecision / ContextualRecall) need it; Faithfulness and
AnswerRelevancy do not, so it is left None where it would just be noise.
"""

from dataclasses import dataclass


@dataclass
class GoldenCase:
    input: str
    category: str  # "direct" | "ambiguous" | "out_of_scope" | "cross_document"
    expected_output: str | None = None


golden_cases = [
    # ---- direct: single-document, clear answer ----
    GoldenCase(
        input="How much does the Pro plan cost per month?",
        category="direct",
        expected_output="The Pro plan costs $49 per month.",
    ),
    GoldenCase(
        input="Which plan includes SSO / SAML login?",
        category="direct",
        expected_output="SSO / SAML login is available only on the Enterprise plan.",
    ),
    GoldenCase(
        input="How long is the free trial and does it need a credit card?",
        category="direct",
        expected_output=(
            "There is a 14-day free trial on the Pro plan, and no credit card is "
            "required to start it."
        ),
    ),
    GoldenCase(
        input="What happens to my data during the grace period after cancelling?",
        category="direct",
        expected_output=(
            "During the 30-day grace period the workspace is read-only: you can export "
            "data but cannot add or edit subscriptions. After 30 days it is permanently "
            "deleted."
        ),
    ),
    GoldenCase(
        input="Does PlanFlow charge overage fees when I exceed a limit?",
        category="direct",
        expected_output=(
            "No. PlanFlow never charges overage fees. You enter an over-limit state "
            "where you cannot add new items until you reduce usage or upgrade."
        ),
    ),

    # ---- ambiguous: more than one reasonable reading ----
    GoldenCase(
        input="What's the response time for priority support?",
        category="ambiguous",
        # Ambiguous because "priority support" means different SLAs on Pro vs
        # Enterprise. A good answer should distinguish the two, not pick one silently.
    ),
    GoldenCase(
        input="If I change my plan, when does it take effect?",
        category="ambiguous",
        # Upgrades are immediate; downgrades are end-of-cycle. "Change" is ambiguous.
    ),
    GoldenCase(
        input="Can I get a refund?",
        category="ambiguous",
        # Depends on how long since the last charge (full within 7 days, else partial).
    ),

    # ---- out_of_scope: not in the docs; must admit, not invent ----
    GoldenCase(
        input="Does PlanFlow integrate with SAP?",
        category="out_of_scope",
    ),
    GoldenCase(
        input="Is there a mobile app for iOS and Android?",
        category="out_of_scope",
    ),
    GoldenCase(
        input="What is PlanFlow's phone number for support?",
        category="out_of_scope",
    ),
    GoldenCase(
        input="Do you offer a discount for non-profit organizations?",
        category="out_of_scope",
    ),

    # ---- cross_document: needs two documents combined ----
    GoldenCase(
        input="I subscribed 3 days ago. If I cancel now, do I get all my money back?",
        category="cross_document",
        expected_output=(
            "Yes. Within 7 days of the most recent charge you get a full refund, and a "
            "full refund cancels the subscription for you. (Note that cancelling alone "
            "does not trigger a refund.)"
        ),
    ),
    GoldenCase(
        input=(
            "I want to downgrade to Basic, but I track more subscriptions than Basic "
            "allows. What happens?"
        ),
        category="cross_document",
        expected_output=(
            "The downgrade is scheduled for the end of the billing period. When it takes "
            "effect, if you are over the Basic limit the workspace enters an over-limit "
            "state: existing data stays readable but you cannot add new subscriptions "
            "until you are back under the limit. The downgrade is not blocked."
        ),
    ),
    GoldenCase(
        input=(
            "If I ask for a partial refund on my annual plan, is my subscription "
            "cancelled too?"
        ),
        category="cross_document",
        expected_output=(
            "No. A partial refund does not cancel the plan by itself. You must also "
            "cancel separately if you want the subscription to end; otherwise it stays "
            "active."
        ),
    ),
    GoldenCase(
        input="How fast is support on the plan that includes audit log export?",
        category="cross_document",
        expected_output=(
            "Audit log export is an Enterprise feature, and Enterprise priority support "
            "has a 1-business-hour response target with a 99.9% uptime SLA."
        ),
    ),
]
