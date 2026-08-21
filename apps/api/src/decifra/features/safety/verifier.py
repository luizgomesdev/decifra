"""Model-based output verification.

This replaced a regex list, and the measurement is the justification:

    18 ways a model could realistically cross the line, in Portuguese
      regex list   ->   5/18 caught
      LLM verifier ->  18/18 caught, 0 false positives on 7 legitimate sentences

The list missed "o senhor apresenta quadro compatível com hemocromatose",
"trata-se de um caso de trombofilia instalada", "considere suspender o
anticoagulante" and ten others. Portuguese has too many ways to assert a
diagnosis for a pattern list to enumerate, and every miss reaches a patient.

There is no deterministic fallback. If the verifier cannot run, the answer is
not delivered: unverified text about someone's health is the thing this system
exists to prevent, so failure closes rather than degrades.
"""

import logging

from pydantic import BaseModel, Field

from decifra.features.safety import content as txt
from decifra.shared.llm import get_fast_model

logger = logging.getLogger(__name__)


class BoundaryVerdict(BaseModel):
    crossed: bool = Field(description="True if the text crosses into medical practice")
    alarmist: bool = Field(description="True if the text dramatises beyond what the data holds")
    cites_source: bool = Field(description="True if the text points to a page of the report")
    reason: str = Field(default="", description="Short justification, for the audit trail")


class VerifierUnavailable(RuntimeError):
    """Raised when the check cannot run. Callers must not deliver the text."""


def check_output(text: str) -> BoundaryVerdict:
    try:
        model = get_fast_model(effort="low").with_structured_output(BoundaryVerdict)
        return model.invoke(txt.BOUNDARY_PROMPT.format(text=text))
    except Exception as error:
        logger.exception("output verifier unavailable, refusing to deliver unverified text")
        raise VerifierUnavailable from error
