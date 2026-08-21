"""Chat state and wire types."""

from typing import Literal

from pydantic import BaseModel, Field

Intent = Literal[
    "report_question", "diagnosis", "prescription", "prognosis", "emergency", "off_topic"
]

REFUSED_INTENTS: dict[str, str] = {
    "diagnosis": "diagnosis",
    "prescription": "prescription",
    "prognosis": "prognosis",
    "emergency": "emergency",
}


class IntentDecision(BaseModel):
    intent: Intent = Field(description="The single category that best fits the question")


class GroundingVerdict(BaseModel):
    grounded: bool = Field(
        description="True only if every claim in the answer is supported by the excerpts"
    )
    reason: str = Field(default="", description="Short justification, for the audit trail")


class Citation(BaseModel):
    title: str
    page: int
    section: str


class HistoryTurn(BaseModel):
    role: Literal["user", "assistant"]
    text: str


class ChatAnswer(BaseModel):
    session_id: str
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    intent: Intent
    refused: bool
    guard_flags: list[str] = Field(default_factory=list)
