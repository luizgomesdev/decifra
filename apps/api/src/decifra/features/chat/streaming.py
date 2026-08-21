"""Server-sent events for the chat.

Streaming raw tokens would put unverified text about someone's health on screen
and take it back a few seconds later. Showing a diagnosis for three seconds and
then retracting it is worse than making the person wait.

So the stream releases **one verified paragraph at a time**: tokens accumulate
in a buffer, and when a paragraph closes it goes through the same verifier the
middleware uses. Approved paragraphs are emitted; a rejected one ends the stream
and the final state decides what the person actually sees.

Perceived latency drops from "nothing for thirty seconds" to "first paragraph in
about five", without ever displaying text that has not been checked.

Stage events come from the graph's own node updates, so the progress line
describes what is really happening rather than a decorative animation.
"""

import json
import logging
from collections.abc import Iterator

from decifra.features.chat import content as txt
from decifra.features.chat.agent import build_agent
from decifra.features.chat.middleware import PatientContext
from decifra.features.chat.service import citations_from
from decifra.features.safety import content as safety_txt
from decifra.features.safety.verifier import VerifierUnavailable, check_output
from decifra.shared.db import thread_id_for

logger = logging.getLogger(__name__)

PARAGRAPH_BREAK = "\n\n"
MIN_PARAGRAPH_CHARS = 40


def _event(name: str, payload: dict) -> str:
    return f"event: {name}\ndata: {json.dumps(payload, ensure_ascii=False)}\n\n"


def _verified(paragraph: str) -> bool:
    """A paragraph only reaches the screen if the verifier clears it."""
    try:
        verdict = check_output(paragraph)
    except VerifierUnavailable:
        return False
    return not verdict.crossed


def stream_answer(question: str, patient_id: str, session_id: str) -> Iterator[str]:
    agent = build_agent()
    config = {"configurable": {"thread_id": thread_id_for(patient_id, session_id)}}

    yield _event("session", {"session_id": session_id})

    buffer, released, blocked = "", "", False
    stage_index = -1

    try:
        for mode, payload in agent.stream(
            {"messages": [{"role": "user", "content": question}]},
            context=PatientContext(patient_id=patient_id),
            config=config,
            stream_mode=["messages", "updates"],
        ):
            if mode == "updates":
                for node in payload:
                    # `model` is announced on its first token instead: node
                    # updates only arrive once the node finishes, which would
                    # put "writing" after the text was already on screen.
                    if node == "model" or node not in txt.STAGE_ORDER:
                        continue
                    if txt.STAGE_ORDER[node] > stage_index:
                        stage_index = txt.STAGE_ORDER[node]
                        yield _event("stage", {"label": txt.STAGE_LABELS[node]})
                continue

            chunk, meta = payload
            # Only the answering model's tokens. The middlewares also call
            # models (classification, verification) and those are not the answer.
            if meta.get("langgraph_node") != "model" or not chunk.text:
                continue

            if stage_index < txt.STAGE_ORDER["model"]:
                stage_index = txt.STAGE_ORDER["model"]
                yield _event("stage", {"label": txt.STAGE_LABELS["model"]})

            buffer += chunk.text
            while PARAGRAPH_BREAK in buffer:
                paragraph, buffer = buffer.split(PARAGRAPH_BREAK, 1)
                if len(paragraph.strip()) < MIN_PARAGRAPH_CHARS:
                    buffer = paragraph + PARAGRAPH_BREAK + buffer
                    break
                if not _verified(paragraph):
                    blocked = True
                    break
                released += paragraph + PARAGRAPH_BREAK
                yield _event("delta", {"text": paragraph + PARAGRAPH_BREAK})
            if blocked:
                break

        if not blocked and buffer.strip() and _verified(buffer):
            released += buffer
            yield _event("delta", {"text": buffer})

    except Exception:
        logger.exception("chat stream failed")
        yield _event(
            "final", {"text": safety_txt.UNVERIFIED, "refused": True, "flags": [], "citations": []}
        )
        return

    state = agent.get_state(config).values
    message = state["messages"][-1]
    yield _event(
        "final",
        {
            "text": message.text,
            "refused": state.get("refused", False),
            "flags": state.get("guard_flags", []),
            "citations": [c.model_dump() for c in citations_from(state.get("documents", []))]
            if not state.get("refused", False)
            else [],
            # The front replaces the streamed text when the final state differs,
            # which happens whenever a guardrail rewrote or replaced the answer.
            "replaced": message.text.strip() != released.strip(),
        },
    )
