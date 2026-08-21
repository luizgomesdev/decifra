"""Chat entry point."""

from langchain_core.documents import Document

from decifra.features.chat.agent import build_agent
from decifra.features.chat.middleware import PatientContext
from decifra.features.chat.schemas import ChatAnswer, Citation, HistoryTurn
from decifra.shared.db import new_session_id, thread_id_for


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
