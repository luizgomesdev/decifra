"""Operational logs carry the outcome, never the content (spec OBS-03, OBS-04)."""

import json
import logging
from types import SimpleNamespace

import pytest

from decifra.features.chat import service
from decifra.shared.logging import log_event

QUESTION = "tenho risco de alzheimer?"


class FakeAgent:
    def invoke(self, *args, **kwargs):
        return {
            "messages": [SimpleNamespace(text="resposta")],
            "intent": "report_question",
            "refused": False,
            "documents": [],
            "guard_flags": [],
        }


class BrokenAgent:
    def invoke(self, *args, **kwargs):
        raise ConnectionError("qdrant down")


def events(caplog):
    return [json.loads(record.message) for record in caplog.records if record.name == "decifra.events"]


def test_log_event_writes_one_json_line(caplog):
    with caplog.at_level(logging.INFO, logger="decifra.events"):
        log_event("chat", request_id="abc123", duration_ms=12)

    assert events(caplog) == [{"event": "chat", "request_id": "abc123", "duration_ms": 12}]


def test_answered_chat_logs_the_outcome(monkeypatch, caplog):
    monkeypatch.setattr(service, "build_agent", lambda: FakeAgent())

    with caplog.at_level(logging.INFO, logger="decifra.events"):
        service.ask(QUESTION, "patient-1", "session-1")

    record = events(caplog)[-1]
    assert record["event"] == "chat"
    assert record["patient_id"] == "patient-1"
    assert record["intent"] == "report_question"
    assert record["refused"] is False
    assert record["duration_ms"] >= 0
    assert record["model"]
    assert record["request_id"]


def test_failed_chat_logs_the_error_type(monkeypatch, caplog):
    monkeypatch.setattr(service, "build_agent", lambda: BrokenAgent())

    with caplog.at_level(logging.INFO, logger="decifra.events"), pytest.raises(ConnectionError):
        service.ask(QUESTION, "patient-1", "session-1")

    record = events(caplog)[-1]
    assert record["event"] == "chat.failed"
    assert record["error"] == "ConnectionError"
    assert record["duration_ms"] >= 0


@pytest.mark.parametrize("agent", [FakeAgent(), BrokenAgent()])
def test_no_record_carries_the_question(monkeypatch, caplog, agent):
    monkeypatch.setattr(service, "build_agent", lambda: agent)

    with caplog.at_level(logging.INFO, logger="decifra.events"):
        try:
            service.ask(QUESTION, "patient-1", "session-1")
        except ConnectionError:
            pass

    assert "alzheimer" not in json.dumps(events(caplog)).lower()
