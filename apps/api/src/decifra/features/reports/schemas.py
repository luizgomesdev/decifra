"""Structured shape of a genetic report.

Every finding carries `source_page`. That is what lets an answer cite where it
came from instead of asserting without backing. A finding without a page is a
finding without provenance, and it should never reach the patient.
"""

from pydantic import BaseModel, Field


class AncestryComponent(BaseModel):
    region: str = Field(description="Geographic region, exactly as printed in the report")
    percentage: str = Field(description="Proportion, including the percent sign")
    detail: str = Field(default="", description="Sub-region detail, when present")


class Ancestry(BaseModel):
    summary: str = Field(description="Summary paragraph of the genomic composition")
    components: list[AncestryComponent]
    maternal_haplogroup: str = ""
    paternal_haplogroup: str = ""
    neanderthal: str = ""
    source_page: int


class RiskFinding(BaseModel):
    condition: str
    gene: str
    variant: str
    genotype: str
    risk_level: str = Field(description="Risk classification as printed in the report")
    relative_risk: str = Field(default="", description="Relative risk, when stated")
    absolute_risk: str = Field(
        default="", description="Plain-numbers explanation of the risk, when present"
    )
    interpretation: str
    recommended_action: str = Field(
        default="", description="Follow-up suggested by the report, when present"
    )
    evidence_source: str = Field(
        default="", description="Literature reference backing the risk figure, when cited"
    )
    source_page: int


class Trait(BaseModel):
    name: str
    gene: str
    variant: str
    result: str
    source_page: int


class Pharmacogenomic(BaseModel):
    drug: str
    gene: str
    genotype: str
    phenotype: str
    note: str = ""
    source_page: int


class GeneticReport(BaseModel):
    patient_id: str = Field(description="Sample identifier, shaped GEN-YYYY-NNNNN")
    patient_name: str
    age: int | None = None
    sex: str = ""
    collection_date: str = ""
    issue_date: str = ""
    ancestry: Ancestry
    risk_findings: list[RiskFinding]
    traits: list[Trait] = Field(default_factory=list)
    pharmacogenomics: list[Pharmacogenomic] = Field(default_factory=list)
