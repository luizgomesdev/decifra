"""Runs the golden cases against the live agent and writes the report.

Separate from pytest on purpose: this hits the API, costs money and takes about
a minute. It is the evidence artifact both enunciados ask for ("resultados dos
testes de qualidade das respostas"), so it writes a markdown table into docs/.

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

from decifra.features.chat.service import ask
from decifra.shared.db import close_pool

OUTPUT = REPO_ROOT / "docs" / "golden-cases.md"
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


def main() -> None:
    results = []
    for case in CASES:
        started = time.monotonic()
        answer = ask(case.question, case.patient_id)
        result = check(case, answer, time.monotonic() - started)
        results.append(result)
        print(f"  {'PASSOU' if not result['failures'] else 'FALHOU'}  {case.name}")

    passed = sum(1 for r in results if not r["failures"])
    lines = [
        "# Testes de qualidade das respostas",
        "",
        (
            "Gerado por `scripts/run_golden.py`. Cada caso declara o que a resposta precisa "
            "conter e o que ela nunca pode conter. As verificações são sobre substância "
            "(genótipo, número, página), não sobre a redação, para que a suíte falhe quando "
            "o conteúdo estiver errado e não quando o texto mudar de forma."
        ),
        "",
        f"**Resultado: {passed} de {len(results)} casos aprovados.**",
        "",
        "| Caso | Pergunta | Paciente | Intenção | Recusa | Guardrails | Tempo | Resultado |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in results:
        case, answer = r["case"], r["answer"]
        flags = ", ".join(answer.guard_flags) or "—"
        status = "aprovado" if not r["failures"] else "**falhou**: " + "; ".join(r["failures"])
        lines.append(
            f"| `{case.name}` | {case.question} | ...{case.patient_id[-5:]} | {answer.intent} "
            f"| {'sim' if answer.refused else 'não'} | {flags} | {r['elapsed']:.1f}s | {status} |"
        )

    lines += ["", "## Respostas na íntegra", ""]
    for r in results:
        lines += [
            f"### {r['case'].name}",
            "",
            f"> {r['case'].question}",
            "",
            "```",
            r["answer"].answer.strip(),
            "```",
            "",
        ]

    OUTPUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"\n{passed}/{len(results)} aprovados. Relatorio em {OUTPUT.relative_to(REPO_ROOT)}")
    close_pool()


if __name__ == "__main__":
    main()
