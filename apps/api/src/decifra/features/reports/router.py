"""Report endpoints: the structured profile behind the dashboard."""

from fastapi import APIRouter, HTTPException

from decifra.features.reports.schemas import GeneticReport
from decifra.features.reports.service import list_reports, load_report
from decifra.features.reports.summary import build_summary, risk_sort_key

router = APIRouter(prefix="/patients", tags=["reports"])


@router.get("")
def list_patients() -> list[dict]:
    return [
        {"patient_id": report.patient_id, "name": report.patient_name, "age": report.age}
        for report in list_reports()
    ]


@router.get("/{patient_id}/report")
def get_report(patient_id: str) -> GeneticReport:
    report = load_report(patient_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Relatório não encontrado")
    # Clinical relevance, not PDF order: an increased risk the patient can act on
    # should not sit below a trait about eye colour.
    report.risk_findings.sort(key=risk_sort_key)
    return report


@router.get("/{patient_id}/summary")
def get_summary(patient_id: str) -> dict:
    report = load_report(patient_id)
    if report is None:
        raise HTTPException(status_code=404, detail="Relatório não encontrado")
    return build_summary(report)
