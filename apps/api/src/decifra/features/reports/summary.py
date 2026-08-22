"""Risk ordering and the automatic report summary.

The summary is a second surface where the model writes about someone's health,
so it goes through the same verifier as the chat instead of trusting its own
prompt. Same failure policy too: unverified means undelivered.
"""

import unicodedata

from decifra.features.reports import content as txt
from decifra.features.reports.schemas import GeneticReport, RiskFinding
from decifra.features.safety import content as safety_txt
from decifra.features.safety.verifier import VerifierUnavailable, check_output
from decifra.shared.llm import get_fast_model

# Lower sorts first. Actionable increased risk leads; everything else follows.
RISK_ORDER = {
    "aumentado": 0,
    "levemente aumentado": 1,
    "compativel": 2,
    "padrao": 3,
    "reduzido": 4,
}


def _fold(text: str) -> str:
    """Strips accents so matching does not depend on how the report spells it.

    Without this, "Compatível com intolerância" misses the "compativel" key and
    the finding drops to the end of the list. The report is written by a human
    and its accents are not a contract.
    """
    stripped = unicodedata.normalize("NFKD", text.strip().lower())
    return "".join(c for c in stripped if not unicodedata.combining(c))


def risk_sort_key(finding: RiskFinding) -> tuple[int, str]:
    level = _fold(finding.risk_level)
    for label, rank in RISK_ORDER.items():
        if level.startswith(label):
            return (rank, finding.condition)
    return (len(RISK_ORDER), finding.condition)


def _facts(report: GeneticReport) -> str:
    findings = sorted(report.risk_findings, key=risk_sort_key)
    lines = [
        txt.SUMMARY["ancestry"].format(
            summary=report.ancestry.summary,
            components=", ".join(
                f"{c.region} {c.percentage}" for c in report.ancestry.components[:4]
            ),
        )
    ]
    lines += [
        txt.SUMMARY["finding"].format(
            condition=finding.condition,
            gene=finding.gene,
            genotype=finding.genotype,
            level=finding.risk_level,
            absolute=finding.absolute_risk or finding.relative_risk,
            page=finding.source_page,
        )
        for finding in findings
    ]
    return "\n".join(lines)


def build_summary(report: GeneticReport) -> dict:
    """Generates the plain-language summary and reports which guards fired."""
    model = get_fast_model(effort="low", verbosity="medium")
    text = model.invoke(txt.SUMMARY["prompt"].format(facts=_facts(report))).text

    flags = []
    try:
        verdict = check_output(text)
    except VerifierUnavailable:
        return {"summary": safety_txt.UNVERIFIED, "guard_flags": ["verifier_unavailable"]}

    if verdict.crossed:
        flags.append("boundary_crossed")
        text = txt.SUMMARY["fallback"]
    elif verdict.alarmist:
        flags.append("alarmist_rewritten")
        text = model.invoke(txt.SUMMARY["rewrite"].format(summary=text)).text

    return {
        "summary": f"{text}\n\n---\n{safety_txt.DISCLAIMER}",
        "guard_flags": flags,
    }
