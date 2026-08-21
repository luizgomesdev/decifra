"""Turns a structured report into retrievable documents.

Chunking is semantic, not blind. A fixed-size splitter would cut a risk finding
in half and let retrieval return a genotype without its interpretation, or a
relative risk without the sentence saying most carriers never develop the
condition. In this domain that truncation is the failure mode we care about
most, so each finding becomes exactly one document.

Every document carries `patient_id` in its payload. Retrieval filters on it,
which is what keeps one patient's report out of another's answers.

Portuguese label templates live in content.py, never inline here.
"""

from langchain_core.documents import Document
from qdrant_client.models import FieldCondition, Filter, FilterSelector, MatchValue

from decifra.config import get_settings
from decifra.features.reports import content as txt
from decifra.features.reports.schemas import GeneticReport
from decifra.shared.vectorstore import get_qdrant_client, get_vector_store

SECTION_ANCESTRY = "ancestry"
SECTION_RISK = "risk"
SECTION_TRAIT = "trait"
SECTION_PHARMACOGENOMICS = "pharmacogenomics"


def _join(lines: list[str]) -> str:
    return "\n".join(line for line in lines if line)


def _ancestry_document(report: GeneticReport) -> Document:
    ancestry = report.ancestry
    components = [
        txt.ANCESTRY["component_with_detail"].format(
            region=c.region, percentage=c.percentage, detail=c.detail
        )
        if c.detail
        else txt.ANCESTRY["component"].format(region=c.region, percentage=c.percentage)
        for c in ancestry.components
    ]
    lines = [
        txt.ANCESTRY["header"],
        ancestry.summary,
        "",
        txt.ANCESTRY["composition"],
        *components,
        txt.ANCESTRY["maternal_haplogroup"].format(value=ancestry.maternal_haplogroup)
        if ancestry.maternal_haplogroup
        else "",
        txt.ANCESTRY["paternal_haplogroup"].format(value=ancestry.paternal_haplogroup)
        if ancestry.paternal_haplogroup
        else "",
        txt.ANCESTRY["neanderthal"].format(value=ancestry.neanderthal)
        if ancestry.neanderthal
        else "",
    ]
    return Document(
        page_content=_join(lines),
        metadata={
            "patient_id": report.patient_id,
            "section": SECTION_ANCESTRY,
            "title": txt.ANCESTRY["title"],
            "page": ancestry.source_page,
        },
    )


def _risk_documents(report: GeneticReport) -> list[Document]:
    documents = []
    for finding in report.risk_findings:
        lines = [
            txt.RISK["condition"].format(value=finding.condition),
            txt.RISK["gene"].format(value=finding.gene),
            txt.RISK["variant"].format(value=finding.variant),
            txt.RISK["genotype"].format(value=finding.genotype),
            txt.RISK["risk_level"].format(value=finding.risk_level),
            txt.RISK["relative_risk"].format(value=finding.relative_risk)
            if finding.relative_risk
            else "",
            txt.RISK["absolute_risk"].format(value=finding.absolute_risk)
            if finding.absolute_risk
            else "",
            txt.RISK["interpretation"].format(value=finding.interpretation),
            txt.RISK["recommended_action"].format(value=finding.recommended_action)
            if finding.recommended_action
            else "",
            txt.RISK["evidence_source"].format(value=finding.evidence_source)
            if finding.evidence_source
            else "",
        ]
        documents.append(
            Document(
                page_content=_join(lines),
                metadata={
                    "patient_id": report.patient_id,
                    "section": SECTION_RISK,
                    "title": finding.condition,
                    "gene": finding.gene,
                    "risk_level": finding.risk_level,
                    "page": finding.source_page,
                },
            )
        )
    return documents


def _trait_documents(report: GeneticReport) -> list[Document]:
    return [
        Document(
            page_content=_join(
                [
                    txt.TRAIT["name"].format(value=trait.name),
                    txt.TRAIT["gene"].format(value=trait.gene),
                    txt.TRAIT["variant"].format(value=trait.variant),
                    txt.TRAIT["result"].format(value=trait.result),
                ]
            ),
            metadata={
                "patient_id": report.patient_id,
                "section": SECTION_TRAIT,
                "title": trait.name,
                "gene": trait.gene,
                "page": trait.source_page,
            },
        )
        for trait in report.traits
    ]


def _pharmacogenomic_documents(report: GeneticReport) -> list[Document]:
    return [
        Document(
            page_content=_join(
                [
                    txt.PHARMACOGENOMICS["drug"].format(value=entry.drug),
                    txt.PHARMACOGENOMICS["gene"].format(value=entry.gene),
                    txt.PHARMACOGENOMICS["genotype"].format(value=entry.genotype),
                    txt.PHARMACOGENOMICS["phenotype"].format(value=entry.phenotype),
                    txt.PHARMACOGENOMICS["note"].format(value=entry.note) if entry.note else "",
                ]
            ),
            metadata={
                "patient_id": report.patient_id,
                "section": SECTION_PHARMACOGENOMICS,
                "title": entry.drug,
                "gene": entry.gene,
                "page": entry.source_page,
            },
        )
        for entry in report.pharmacogenomics
    ]


def build_documents(report: GeneticReport) -> list[Document]:
    return [
        _ancestry_document(report),
        *_risk_documents(report),
        *_trait_documents(report),
        *_pharmacogenomic_documents(report),
    ]


def delete_existing(patient_id: str) -> None:
    """Drops a patient's points so re-ingestion does not pile up duplicates."""
    get_qdrant_client().delete(
        collection_name=get_settings().qdrant_collection,
        points_selector=FilterSelector(
            filter=Filter(
                must=[FieldCondition(key="metadata.patient_id", match=MatchValue(value=patient_id))]
            )
        ),
    )


def index_report(report: GeneticReport) -> int:
    store = get_vector_store()
    delete_existing(report.patient_id)
    documents = build_documents(report)
    store.add_documents(documents)
    return len(documents)
