"""Agent assembly.

No tools: retrieval is middleware, not a tool the model may skip. See the
docstring in middleware.py for why.
"""

from functools import lru_cache

from langchain.agents import create_agent
from langchain.agents.middleware import PIIMiddleware

from decifra.features.chat.middleware import (
    CPF_PATTERN,
    ClinicalBoundaryMiddleware,
    DecifraState,
    DisclaimerMiddleware,
    GroundingMiddleware,
    IntentGuardMiddleware,
    PatientContext,
    RetrievalMiddleware,
)
from decifra.shared.db import get_checkpointer
from decifra.shared.llm import get_reasoning_model


def middleware_stack() -> list:
    """The guardrail order, as a value so it can be asserted in a test."""
    return [
        IntentGuardMiddleware(),
        PIIMiddleware("cpf", detector=CPF_PATTERN, strategy="redact", apply_to_input=True),
        PIIMiddleware("email", strategy="redact", apply_to_input=True),
        RetrievalMiddleware(),
        ClinicalBoundaryMiddleware(),
        # `after_*` hooks run in reverse order, so the disclaimer is listed
        # before grounding to end up running after it. Listed the other way
        # round, a grounding block replaces the message and drops the notice.
        DisclaimerMiddleware(),
        GroundingMiddleware(),
    ]


@lru_cache
def build_agent():
    return create_agent(
        model=get_reasoning_model(effort="medium", verbosity="medium"),
        tools=[],
        middleware=middleware_stack(),
        state_schema=DecifraState,
        context_schema=PatientContext,
        checkpointer=get_checkpointer(),
    )
