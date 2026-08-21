"""Ingestion entry points: PDF in, indexed and persisted report out."""

import json
from pathlib import Path

from decifra.config import get_settings
from decifra.features.reports.indexer import index_report
from decifra.features.reports.parser import parse_report
from decifra.features.reports.schemas import GeneticReport


def structured_path(patient_id: str) -> Path:
    return get_settings().reports_dir / "structured" / f"{patient_id}.json"


def load_report(patient_id: str) -> GeneticReport | None:
    path = structured_path(patient_id)
    if not path.exists():
        return None
    return GeneticReport.model_validate_json(path.read_text(encoding="utf-8"))


def list_reports() -> list[GeneticReport]:
    directory = get_settings().reports_dir / "structured"
    return [
        GeneticReport.model_validate_json(path.read_text(encoding="utf-8"))
        for path in sorted(directory.glob("*.json"))
    ]


def ingest_pdf(pdf_path: Path) -> tuple[GeneticReport, int]:
    """Parses, persists and indexes one report. Returns it with the chunk count."""
    report = parse_report(pdf_path)

    path = structured_path(report.patient_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report.model_dump(), ensure_ascii=False, indent=2), encoding="utf-8")

    chunks = index_report(report)
    return report, chunks
