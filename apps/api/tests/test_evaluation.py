"""Consistency aggregation of the evaluation run (spec EVA-02)."""

import importlib.util
from pathlib import Path
from types import SimpleNamespace

import pytest

REPO_ROOT = Path(__file__).resolve().parents[3]


@pytest.fixture(scope="module")
def evaluation():
    spec = importlib.util.spec_from_file_location("run_golden", REPO_ROOT / "scripts" / "run_golden.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(failures, elapsed=1.0):
    return {"failures": failures, "elapsed": elapsed, "answer": SimpleNamespace(refused=False)}


def test_all_runs_passing_is_consistent(evaluation):
    summary = evaluation.summarise(SimpleNamespace(name="case"), [run([]), run([]), run([])])

    assert summary["passes"] == 3
    assert summary["runs"] == 3
    assert summary["consistent"] is True
    assert summary["average_ms"] == 1000


def test_a_case_that_changes_result_is_flagged(evaluation):
    summary = evaluation.summarise(
        SimpleNamespace(name="case"), [run([]), run(["faltou `pagina`"]), run([])]
    )

    assert summary["passes"] == 2
    assert summary["consistent"] is False
    assert summary["failures"] == ["faltou `pagina`"]


def test_all_runs_failing_is_consistent_too(evaluation):
    summary = evaluation.summarise(SimpleNamespace(name="case"), [run(["erro"]), run(["erro"])])

    assert summary["passes"] == 0
    assert summary["consistent"] is True
