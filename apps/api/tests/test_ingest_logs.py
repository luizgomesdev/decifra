"""The ingestion pipeline reports what it did (spec OBS-05)."""

import importlib.util
import json
import logging
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]


def load_ingest():
    spec = importlib.util.spec_from_file_location("ingest_script", REPO_ROOT / "scripts" / "ingest.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.fixture
def pipeline(tmp_path, monkeypatch):
    module = load_ingest()
    inbox = tmp_path / "inbox"
    inbox.mkdir()
    (inbox / "laudo-1.pdf").write_bytes(b"%PDF-1.4")
    monkeypatch.setattr(module, "inbox", lambda: inbox)
    monkeypatch.setattr(module, "processed", lambda: tmp_path / "processed")
    return module


def events(caplog):
    return [json.loads(record.message) for record in caplog.records if record.name == "decifra.events"]


def test_a_processed_report_is_logged(pipeline, monkeypatch, caplog):
    monkeypatch.setattr(
        pipeline, "ingest_pdf", lambda path: (SimpleNamespace(patient_id="patient-1"), 7)
    )

    with caplog.at_level(logging.INFO, logger="decifra.events"):
        processed = pipeline.ingest_new()

    start, report = events(caplog)
    assert processed == 1
    assert start == {"event": "ingest.started", "reports": 1}
    assert report["event"] == "ingest.report"
    assert report["patient_id"] == "patient-1"
    assert report["chunks"] == 7
    assert report["duration_ms"] >= 0


def test_a_failing_report_is_logged_and_the_batch_continues(pipeline, monkeypatch, caplog):
    def explode(path):
        raise ValueError("corrupted pdf")

    monkeypatch.setattr(pipeline, "ingest_pdf", explode)

    with caplog.at_level(logging.INFO, logger="decifra.events"):
        processed = pipeline.ingest_new()

    failure = events(caplog)[-1]
    assert processed == 0
    assert failure["event"] == "ingest.failed"
    assert failure["error"] == "ValueError"
    assert failure["report"] == "laudo-1.pdf"
