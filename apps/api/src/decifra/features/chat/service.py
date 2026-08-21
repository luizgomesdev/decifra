"""Chat entry point."""

from langchain_core.documents import Document

from decifra.features.chat import content as txt
from decifra.features.chat.agent import build_agent
from decifra.features.chat.middleware import PatientContext
from decifra.features.chat.schemas import ChatAnswer, Citation, HistoryTurn
from decifra.features.safety import content as safety_txt
from decifra.features.safety.verifier import VerifierUnavailable, check_output
from decifra.shared.db import new_session_id, thread_id_for
from decifra.shared.llm import get_fast_model


def citations_from(documents: list[Document]) -> list[Citation]:
    seen, citations = set(), []
    for doc in documents:
        key = (doc.metadata.get("title"), doc.metadata.get("page"))
        if key in seen:
            continue
        seen.add(key)
        citations.append(
            Citation(
                title=doc.metadata.get("title", ""),
                page=int(doc.metadata.get("page", 0)),
                section=doc.metadata.get("section", ""),
            )
        )
    return citations


def ask(question: str, patient_id: str, session_id: str | None = None) -> ChatAnswer:
    session_id = session_id or new_session_id()
    result = build_agent().invoke(
        {"messages": [{"role": "user", "content": question}]},
        context=PatientContext(patient_id=patient_id),
        config={"configurable": {"thread_id": thread_id_for(patient_id, session_id)}},
    )
    refused = result.get("refused", False)
    return ChatAnswer(
        session_id=session_id,
        answer=result["messages"][-1].text,
        citations=[] if refused else citations_from(result.get("documents", [])),
        intent=result.get("intent", "report_question"),
        refused=refused,
        guard_flags=result.get("guard_flags", []),
    )


def history(patient_id: str, session_id: str) -> list[HistoryTurn]:
    """Conversation so far, straight from the checkpointer."""
    state = build_agent().get_state(
        {"configurable": {"thread_id": thread_id_for(patient_id, session_id)}}
    )
    messages = state.values.get("messages", []) if state.values else []
    return [
        HistoryTurn(role="user" if message.type == "human" else "assistant", text=message.text)
        for message in messages
        if message.type in ("human", "ai") and message.text
    ]


def summarise_conversation(patient_id: str, session_id: str) -> dict:
    """Recaps a session so the person can pick it up later.

    Regenerated from the stored turns rather than kept incrementally: the
    checkpointer is already the source of truth, and an incremental summary
    would drift from it.

    Goes through the same verifier as every other generated text. A recap is
    still the model writing about someone's health.
    """
    turns = history(patient_id, session_id)
    if not turns:
        return {"summary": txt.CONVERSATION_SUMMARY["empty"], "guard_flags": [], "turns": 0}

    conversation = "\n".join(
        txt.CONVERSATION_SUMMARY["turn"].format(
            role=txt.CONVERSATION_SUMMARY["roles"][turn.role], text=turn.text
        )
        for turn in turns
    )
    model = get_fast_model(effort="low", verbosity="low")
    text = model.invoke(txt.CONVERSATION_SUMMARY["prompt"].format(conversation=conversation)).text

    try:
        verdict = check_output(text)
    except VerifierUnavailable:
        return {
            "summary": safety_txt.UNVERIFIED,
            "guard_flags": ["verifier_unavailable"],
            "turns": len(turns),
        }

    if verdict.crossed:
        return {
            "summary": safety_txt.UNVERIFIED,
            "guard_flags": ["boundary_crossed"],
            "turns": len(turns),
        }

    return {"summary": text, "guard_flags": [], "turns": len(turns)}
