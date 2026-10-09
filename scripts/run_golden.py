"""Runs the golden cases against the live agent and writes the reports.

Separate from pytest on purpose: this hits the API, costs money and takes a few
minutes. Each case runs three times, because a model that answers well once and
badly the next time is not ready for anyone to rely on. The run writes the case
by case report and the evaluation summary into docs/.

    cd apps/api && uv run python ../../scripts/run_golden.py
"""

import re
import sys
import time
import unicodedata
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "apps" / "api" / "src"))
sys.path.insert(0, str(REPO_ROOT / "apps" / "api" / "tests"))

from golden_cases import CASES, GoldenCase

from decifra.config import get_settings
from decifra.features.chat.service import ask
from decifra.shared.db import close_pool

CASES_REPORT = REPO_ROOT / "docs" / "golden-cases.md"
EVALUATION_REPORT = REPO_ROOT / "docs" / "evaluation.md"
RUNS = 3
CITATION = re.compile(r"paginas?\s+\d+")


def normalise(text: str) -> str:
    stripped = unicodedata.normalize("NFKD", text.lower())
    return "".join(c for c in stripped if not unicodedata.combining(c))


def check(case: GoldenCase, answer, elapsed: float) -> dict:
    body = normalise(answer.answer)
    failures = []

    if answer.intent != case.expected_intent:
        failures.append(f"intent {answer.intent}, esperado {case.expected_intent}")
    if answer.refused != case.should_refuse:
        failures.append(f"refused {answer.refused}, esperado {case.should_refuse}")
    for slot in case.must_include:
        if not any(normalise(option) in body for option in slot):
            failures.append(f"faltou `{' ou '.join(slot)}`")
    for forbidden in case.must_not_include:
        if normalise(forbidden) in body:
            failures.append(f"vazou `{forbidden}`")
    if case.requires_citation and not CITATION.search(body):
        failures.append("sem citacao de pagina no texto")

    return {"case": case, "answer": answer, "failures": failures, "elapsed": elapsed}


def summarise(case, results: list[dict]) -> dict:
    """One line per case: how many runs passed and how long they took."""
    passes = sum(1 for result in results if not result["failures"])
    return {
        "case": case,
        "passes": passes,
        "runs": len(results),
        "consistent": passes in (0, len(results)),
        "average_ms": int(sum(result["elapsed"] for result in results) / len(results) * 1000),
        "failures": sorted({failure for result in results for failure in result["failures"]}),
        "answer": results[-1]["answer"],
    }


def write_cases_report(summaries: list[dict]) -> None:
    approved = sum(1 for summary in summaries if summary["passes"] == summary["runs"])
    lines = [
        "# Testes de qualidade das respostas",
        "",
        (
            "Gerado por `scripts/run_golden.py`. Cada caso declara o que a resposta precisa "
            "conter e o que ela nunca pode conter, e roda "
            f"{RUNS} vezes. As verificações são sobre substância (genótipo, número, página), "
            "não sobre a redação."
        ),
        "",
        f"**Resultado: {approved} de {len(summaries)} casos aprovados nas {RUNS} execuções.**",
        "",
        "| Caso | Pergunta | Paciente | Aprovações | Tempo médio | Resultado |",
        "|---|---|---|---|---|---|",
    ]
    for summary in summaries:
        case = summary["case"]
        status = "aprovado" if not summary["failures"] else "**falhou**: " + "; ".join(summary["failures"])
        lines.append(
            f"| `{case.name}` | {case.question} | ...{case.patient_id[-5:]} "
            f"| {summary['passes']}/{summary['runs']} | {summary['average_ms']} ms | {status} |"
        )

    lines += ["", "## Respostas na íntegra", ""]
    for summary in summaries:
        lines += [
            f"### {summary['case'].name}",
            "",
            f"> {summary['case'].question}",
            "",
            "```",
            summary["answer"].answer.strip(),
            "```",
            "",
        ]
    CASES_REPORT.write_text("\n".join(lines), encoding="utf-8")


def write_evaluation_report(summaries: list[dict]) -> None:
    settings = get_settings()
    approved = sum(1 for summary in summaries if summary["passes"] == summary["runs"])
    unstable = [s for s in summaries if not s["consistent"]]
    refusals = [s for s in summaries if s["answer"].refused]
    flags = sorted({flag for s in summaries for flag in s["answer"].guard_flags})
    average = int(sum(s["average_ms"] for s in summaries) / len(summaries))

    lines = [
        "# Avaliação do modelo",
        "",
        (
            f"Execução de {time.strftime('%d/%m/%Y')} contra o agente em funcionamento, "
            f"{RUNS} execuções por caso."
        ),
        "",
        "| Medida | Resultado |",
        "|---|---|",
        f"| Casos avaliados | {len(summaries)} |",
        f"| Execuções por caso | {RUNS} |",
        f"| Casos aprovados em todas as execuções | {approved} de {len(summaries)} |",
        f"| Casos com resultado instável entre execuções | {len(unstable)} |",
        f"| Tempo médio de resposta | {average} ms |",
        f"| Respostas recusadas pelas salvaguardas | {len(refusals)} |",
        f"| Modelo de resposta | `{settings.openai_reasoning_model}` |",
        f"| Modelo de classificação e verificação | `{settings.openai_fast_model}` |",
        "",
        "## Consistência",
        "",
    ]
    if unstable:
        lines.append("Casos que mudaram de resultado entre execuções:")
        lines.append("")
        for summary in unstable:
            lines.append(
                f"- `{summary['case'].name}`: {summary['passes']} de {summary['runs']} execuções "
                f"aprovadas. {'; '.join(summary['failures'])}"
            )
    else:
        lines.append(
            f"Nenhum caso mudou de resultado entre as {RUNS} execuções: cada caso passou "
            "todas as vezes ou falhou todas as vezes."
        )

    lines += [
        "",
        "## Validação das respostas",
        "",
        "Toda resposta passa pelo verificador de fronteira clínica antes de chegar ao paciente, "
        "e a política é fail-closed: sem verificação, nada é entregue. Nesta execução "
        f"{len(refusals)} resposta(s) foram recusadas e as salvaguardas acionadas foram: "
        + (", ".join(f"`{flag}`" for flag in flags) if flags else "nenhuma")
        + ".",
        "",
        (
            "O detalhe caso a caso, com as respostas na íntegra, está em "
            "[golden-cases.md](golden-cases.md)."
        ),
        "",
    ]
    EVALUATION_REPORT.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    summaries = []
    for case in CASES:
        results = []
        for _ in range(RUNS):
            started = time.monotonic()
            answer = ask(case.question, case.patient_id)
            results.append(check(case, answer, time.monotonic() - started))
        summary = summarise(case, results)
        summaries.append(summary)
        print(f"  {summary['passes']}/{RUNS}  {case.name}", flush=True)

    write_cases_report(summaries)
    write_evaluation_report(summaries)

    approved = sum(1 for summary in summaries if summary["passes"] == summary["runs"])
    print(f"\n{approved}/{len(summaries)} casos aprovados em {RUNS} execuções.")
    print(f"Relatorios em {CASES_REPORT.relative_to(REPO_ROOT)} e {EVALUATION_REPORT.relative_to(REPO_ROOT)}")
    close_pool()


if __name__ == "__main__":
    main()
