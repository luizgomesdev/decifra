"""Ingests reports from the inbox folder.

This is the automated indexing path both enunciados ask for: a report dropped
into `data/reports/inbox/` reaches the vector base without anyone running a
step by hand.

    cd apps/api && uv run python ../../scripts/ingest.py          # once
    cd apps/api && uv run python ../../scripts/ingest.py --watch  # keep watching

Watching is plain polling on purpose. A filesystem-event library would add a
dependency to save a few seconds of latency on a pipeline whose slowest step is
a minute of document conversion.

Processed files move to `processed/`, which is what makes re-runs idempotent.
Checking "is there already a JSON for this file" does not work: the JSON is named
after the patient id parsed from inside the document, not after the file, so the
same report under a new filename would be re-ingested forever.
"""

import argparse
import logging
import sys
import time
from pathlib import Path
from time import perf_counter

REPO_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO_ROOT / "apps" / "api" / "src"))

from decifra.config import get_settings
from decifra.features.reports.service import ingest_pdf
from decifra.shared.db import close_pool
from decifra.shared.logging import elapsed_ms, log_event

POLL_SECONDS = 5


def inbox() -> Path:
    return get_settings().reports_dir / "inbox"


def processed() -> Path:
    return get_settings().reports_dir / "processed"


def ingest_new() -> int:
    destination = processed()
    destination.mkdir(parents=True, exist_ok=True)

    pending = sorted(inbox().glob("*.pdf"))
    log_event("ingest.started", reports=len(pending))

    count = 0
    for pdf_path in pending:
        started = perf_counter()
        try:
            report, chunks = ingest_pdf(pdf_path)
        except Exception as error:  # noqa: BLE001 - any failure is a failed report, not a crash
            # One bad report must not take the batch down: log it and move on.
            log_event(
                "ingest.failed",
                report=pdf_path.name,
                error=type(error).__name__,
                duration_ms=elapsed_ms(started),
            )
            continue
        pdf_path.rename(destination / pdf_path.name)
        log_event(
            "ingest.report",
            report=pdf_path.name,
            patient_id=report.patient_id,
            chunks=chunks,
            duration_ms=elapsed_ms(started),
        )
        count += 1
    return count


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--watch", action="store_true", help="observa a pasta continuamente")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(message)s")

    try:
        if not args.watch:
            count = ingest_new()
            print("nenhum laudo novo" if not count else f"{count} laudo(s) processado(s)")
            return

        print(f"observando {inbox()} a cada {POLL_SECONDS}s. Ctrl+C para sair.")
        while True:
            ingest_new()
            time.sleep(POLL_SECONDS)
    except KeyboardInterrupt:
        print("\nencerrado")
    finally:
        close_pool()


if __name__ == "__main__":
    main()
