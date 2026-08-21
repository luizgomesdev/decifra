"""Guardrails as middleware, layered.

LangChain's own guardrail guidance stacks layers rather than picking one
mechanism, and the order matters:

1. `IntentGuardMiddleware` (before_agent) stops a request for a diagnosis,
   prescription or prognosis before it reaches retrieval or the expensive model.
   The reply is a fixed text a human wrote, so it can be audited and cannot
   drift between runs.
2. `PIIMiddleware` (framework, input) redacts identifiers the patient may type
   into the chat. The built-in detectors do not cover CPF, so that one is a
   custom regex.
3. `RetrievalMiddleware` (before_model) always retrieves, always filtered by
   patient. Retrieval is deliberately not a tool: a tool lets the model decide
   whether to look at the report, and answering about someone's genome without
   reading it is the one thing this system must never do.
4. `ClinicalBoundaryMiddleware` (after_model) checks the generated text with a
   separate model, regardless of what the prompt told the generator. It used to
   be a regex list; measurement showed the list caught 5 of 18 realistic
   violations and the verifier caught 18, so the list is gone. If the verifier
   cannot run, nothing is delivered. See safety/verifier.py.
5. `GroundingMiddleware` (after_agent) is model-based, and only runs on text
   that already survived the deterministic layer. It catches what regex cannot:
   an answer that is fluent, unalarming and simply not supported by the report.
6. `DisclaimerMiddleware` (after_agent) appends the notice to every reply,
   including refusals. It is listed *before* grounding because `after_*` hooks
   run in reverse order, so listing it last would let a grounding block drop it.
"""

from dataclasses import dataclass
from typing import Any

from langchain.agents.middleware import AgentMiddleware, AgentState, hook_config
from langchain.messages import AIMessage
from langchain_core.documents import Document
from langgraph.runtime import Runtime
from qdrant_client.models import FieldCondition, Filter, MatchValue

from decifra.features.chat import content as txt
from decifra.features.chat.schemas import REFUSED_INTENTS, GroundingVerdict, IntentDecision
from decifra.features.safety import content as safety_txt
from decifra.features.safety.verifier import VerifierUnavailable, check_output
from decifra.shared.llm import get_fast_model
from decifra.shared.vectorstore import get_vector_store

RETRIEVAL_TOP_K = 5

# The framework ships detectors for email, credit_card, ip, mac_address and url.
# None of those is the identifier that matters in Brazilian health data.
CPF_PATTERN = r"\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b"


@dataclass
class PatientContext:
    """Runtime context. The patient is set by the caller, never by the model."""

    patient_id: str


class DecifraState(AgentState):
    documents: list[Document]
    guard_flags: list[str]
    intent: str
    refused: bool


class IntentGuardMiddleware(AgentMiddleware):
    """Layer 1: refuse out-of-boundary requests before spending anything."""

    state_schema = DecifraState

    @hook_config(can_jump_to=["end"])
    def before_agent(self, state: DecifraState, runtime: Runtime) -> dict[str, Any] | None:
        question = state["messages"][-1].text
        model = get_fast_model(effort="low").with_structured_output(IntentDecision)
        intent = model.invoke(txt.INTENT_PROMPT.format(question=question)).intent

        if intent == "report_question":
            return {"intent": intent, "refused": False, "guard_flags": []}

        answer = (
            txt.OFF_TOPIC if intent == "off_topic" else safety_txt.REFUSALS[REFUSED_INTENTS[intent]]
        )
        return {
            "messages": [AIMessage(answer)],
            "jump_to": "end",
            "intent": intent,
            "refused": True,
            "guard_flags": ["refused_by_intent"],
        }


class RetrievalMiddleware(AgentMiddleware):
    """Layer 3: retrieval that always runs and is always scoped to one patient."""

    state_schema = DecifraState

    def before_model(self, state: DecifraState, runtime: Runtime) -> dict[str, Any] | None:
        patient_id = runtime.context.patient_id
        documents = get_vector_store().similarity_search(
            state["messages"][-1].text,
            k=RETRIEVAL_TOP_K,
            filter=Filter(
                must=[FieldCondition(key="metadata.patient_id", match=MatchValue(value=patient_id))]
            ),
        )
        return {"documents": documents}

    def wrap_model_call(self, request, handler):
        documents = request.state.get("documents", [])
        request.system_message = txt.ANSWER_SYSTEM.format(context=format_context(documents))
        return handler(request)


class ClinicalBoundaryMiddleware(AgentMiddleware):
    """Layer 4: deterministic. Runs whatever the prompt told the model."""

    state_schema = DecifraState

    @hook_config(can_jump_to=["end"])
    def after_model(self, state: DecifraState, runtime: Runtime) -> dict[str, Any] | None:
        message = state["messages"][-1]
        if not isinstance(message, AIMessage) or not message.text:
            return None

        try:
            verdict = check_output(message.text)
        except VerifierUnavailable:
            return {
                "messages": [AIMessage(safety_txt.UNVERIFIED, id=message.id)],
                "jump_to": "end",
                "refused": True,
                "guard_flags": [*state.get("guard_flags", []), "verifier_unavailable"],
            }

        if verdict.crossed:
            # A clinical-boundary breach is replaced, never softened.
            return {
                # Same id replaces the message; a new id would append and the
                # blocked text would stay in history next to its replacement.
                "messages": [AIMessage(safety_txt.REFUSALS["diagnosis"], id=message.id)],
                "jump_to": "end",
                "refused": True,
                "guard_flags": [*state.get("guard_flags", []), "forbidden_language"],
            }

        answer, flags = message.text, list(state.get("guard_flags", []))
        if verdict.alarmist:
            flags.append("alarmist_rewritten")
            rewriter = get_fast_model(effort="low", verbosity="medium")
            answer = rewriter.invoke(txt.REWRITE_PROMPT.format(answer=answer)).text

        if state.get("documents") and not verdict.cites_source:
            flags.append("citation_appended")
            first = state["documents"][0].metadata
            answer += "\n\n" + safety_txt.SOURCE_LABEL.format(
                title=first.get("title", ""), page=first.get("page", "?")
            )

        if answer == message.text:
            return {"guard_flags": flags}
        return {"messages": [AIMessage(answer, id=message.id)], "guard_flags": flags}


class GroundingMiddleware(AgentMiddleware):
    """Layer 5: model-based. Catches fluent answers the report does not support."""

    state_schema = DecifraState

    def after_agent(self, state: DecifraState, runtime: Runtime) -> dict[str, Any] | None:
        if state.get("refused") or not state.get("documents"):
            return None

        message = state["messages"][-1]
        if not isinstance(message, AIMessage) or not message.text:
            return None

        verifier = get_fast_model(effort="low").with_structured_output(GroundingVerdict)
        verdict = verifier.invoke(
            txt.GROUNDING_PROMPT.format(
                context=format_context(state["documents"]), answer=message.text
            )
        )
        if verdict.grounded:
            return None

        return {
            "messages": [AIMessage(safety_txt.UNGROUNDED, id=message.id)],
            "refused": True,
            "guard_flags": [*state.get("guard_flags", []), "ungrounded"],
        }


class DisclaimerMiddleware(AgentMiddleware):
    """Layer 6: the notice goes on every reply, refusals included."""

    state_schema = DecifraState

    def after_agent(self, state: DecifraState, runtime: Runtime) -> dict[str, Any] | None:
        message = state["messages"][-1]
        if not isinstance(message, AIMessage) or safety_txt.DISCLAIMER in message.text:
            return None
        return {
            "messages": [
                AIMessage(f"{message.text}\n\n---\n{safety_txt.DISCLAIMER}", id=message.id)
            ]
        }


def format_context(documents: list[Document]) -> str:
    if not documents:
        return txt.NO_CONTEXT
    return "\n\n".join(
        txt.CONTEXT_ENTRY.format(
            title=doc.metadata.get("title", ""),
            page=doc.metadata.get("page", "?"),
            content=doc.page_content,
        )
        for doc in documents
    )
