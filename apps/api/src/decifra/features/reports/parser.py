"""Turns a report PDF into the structured shape defined in schemas.py.

Two decisions worth stating, because both enunciados ask for the justification.

**Docling instead of a plain text extractor.** A genetic report is mostly
tables: genotype, risk class and relative risk sit in a grid where the column a
value belongs to *is* its meaning. A linear extractor flattens that into
`Campo Valor Gene F5 Variante rs6025 ...` and hands the model the job of guessing
which value belongs to which field. Docling's TableFormer keeps the grid, so the
model reads an actual table.

**LLM extraction instead of regex.** We control the layout of the synthetic
reports, so regex would work here and break on the first real Genera report,
whose layout we do not control. Structured output enforces the schema either way.

Pages come from Docling's own pagination rather than from the model: markdown is
exported page by page and stamped with a marker, so `source_page` is
transcribed, not inferred.
"""

from functools import lru_cache
from pathlib import Path

from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TableFormerMode
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling_core.types.doc import DoclingDocument

from decifra.features.reports.schemas import GeneticReport
from decifra.shared.llm import get_reasoning_model

PAGE_MARKER = "\n\n===== PAGE {page} =====\n"

EXTRACTION_PROMPT = """You extract structured data from Brazilian genetic \
reports (Genera / Dasa). The text below is markdown converted from the original \
PDF, split by page markers shaped `===== PAGE N =====`. Tables are preserved as \
markdown tables.

Rules:
- Copy values exactly as printed. Do not translate, normalise or reword them.
- `source_page` is the number of the page marker the content appears under. \
Transcribe it, never guess it.
- Never infer, complete or improve on what is written. A field with no \
corresponding text in the report stays empty.
- Extract every risk finding, trait and pharmacogenomic entry present, not just \
the notable ones.

Report:

{text}"""


@lru_cache
def get_converter() -> DocumentConverter:
    """Cached: building the converter loads the layout and table models."""
    options = PdfPipelineOptions(do_table_structure=True)
    options.table_structure_options.mode = TableFormerMode.ACCURATE
    options.table_structure_options.do_cell_matching = True
    return DocumentConverter(
        format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=options)}
    )


def convert(pdf_path: Path) -> DoclingDocument:
    return get_converter().convert(str(pdf_path)).document


def build_source_text(document: DoclingDocument) -> str:
    """Exports markdown one page at a time, each under its own page marker."""
    return "".join(
        PAGE_MARKER.format(page=page_no) + document.export_to_markdown(page_no=page_no)
        for page_no in sorted(document.pages)
    )


def parse_report(pdf_path: Path) -> GeneticReport:
    # Higher effort: one pass over a whole document, and a mis-transcribed
    # genotype is a defect that propagates into every later answer.
    model = get_reasoning_model(effort="high").with_structured_output(GeneticReport)
    source_text = build_source_text(convert(pdf_path))
    return model.invoke(EXTRACTION_PROMPT.format(text=source_text))
