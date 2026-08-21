"""Model factories, one per role.

Reasoning effort is set per role rather than globally. OpenAI's own guidance is
to treat effort as a last-mile knob and to get the instructions right first, so
these values are deliberately modest: `low` wherever the task is classification
or rewriting, `medium` only where the model has to reason over retrieved context
and stay inside clinical boundaries.

Verbosity is pinned too. A patient reading about their own genome does not need
a wall of text, and an over-long answer buries the one sentence that matters.
"""

from functools import lru_cache

from langchain_openai import ChatOpenAI, OpenAIEmbeddings

from decifra.config import get_settings


@lru_cache
def get_reasoning_model(effort: str = "medium", verbosity: str = "medium") -> ChatOpenAI:
    """Grounded answers over the report. Accuracy matters more than cost here."""
    settings = get_settings()
    return ChatOpenAI(
        model=settings.openai_reasoning_model,
        api_key=settings.openai_api_key,
        reasoning_effort=effort,
        verbosity=verbosity,
    )


@lru_cache
def get_fast_model(effort: str = "low", verbosity: str = "low") -> ChatOpenAI:
    """Classification and rewriting. High volume, low cost, shallow reasoning."""
    settings = get_settings()
    return ChatOpenAI(
        model=settings.openai_fast_model,
        api_key=settings.openai_api_key,
        reasoning_effort=effort,
        verbosity=verbosity,
    )


@lru_cache
def get_embeddings() -> OpenAIEmbeddings:
    settings = get_settings()
    return OpenAIEmbeddings(model=settings.openai_embedding_model, api_key=settings.openai_api_key)
