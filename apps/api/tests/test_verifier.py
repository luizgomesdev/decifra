"""Verifier behaviour that does not need the API.

There is no deterministic guard any more, so what must be tested here is the
failure policy: when the check cannot run, nothing gets delivered.
"""

import pytest

from decifra.features.safety import verifier


def _break_model(monkeypatch):
    def explode(*args, **kwargs):
        raise RuntimeError("api down")

    monkeypatch.setattr(verifier, "get_fast_model", explode)


def test_unavailable_verifier_raises_instead_of_passing_text_through(monkeypatch):
    _break_model(monkeypatch)
    with pytest.raises(verifier.VerifierUnavailable):
        verifier.check_output("Voce tem Alzheimer.")


def test_chat_refuses_when_verifier_is_unavailable(monkeypatch):
    from langchain.messages import AIMessage

    from decifra.features.chat.middleware import ClinicalBoundaryMiddleware
    from decifra.features.safety import content as safety_txt

    monkeypatch.setattr(
        "decifra.features.chat.middleware.check_output",
        lambda text: (_ for _ in ()).throw(verifier.VerifierUnavailable()),
    )
    state = {"messages": [AIMessage("qualquer texto", id="m1")], "guard_flags": []}
    result = ClinicalBoundaryMiddleware().after_model(state, None)

    assert result["refused"] is True
    assert result["jump_to"] == "end"
    assert "verifier_unavailable" in result["guard_flags"]
    assert result["messages"][0].text == safety_txt.UNVERIFIED


def test_summary_refuses_when_verifier_is_unavailable(monkeypatch):
    from decifra.features.reports import summary
    from decifra.features.safety import content as safety_txt

    monkeypatch.setattr(
        summary, "check_output", lambda text: (_ for _ in ()).throw(verifier.VerifierUnavailable())
    )
    monkeypatch.setattr(
        summary,
        "get_fast_model",
        lambda **kw: type(
            "M", (), {"invoke": lambda self, prompt: type("R", (), {"text": "resumo"})()}
        )(),
    )
    monkeypatch.setattr(summary, "_facts", lambda report: "fatos")

    result = summary.build_summary(report=None)
    assert result["summary"] == safety_txt.UNVERIFIED
    assert result["guard_flags"] == ["verifier_unavailable"]


def test_disclaimer_survives_a_grounding_block():
    """`after_*` hooks run in reverse, so ordering here is load-bearing."""
    from decifra.features.chat.agent import middleware_stack
    from decifra.features.chat.middleware import DisclaimerMiddleware, GroundingMiddleware

    names = [type(m).__name__ for m in middleware_stack()]
    assert names.index(DisclaimerMiddleware.__name__) < names.index(GroundingMiddleware.__name__), (
        "DisclaimerMiddleware must be listed before GroundingMiddleware"
    )
