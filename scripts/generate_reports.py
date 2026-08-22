"""Renders the synthetic reports as PDFs into data/reports/inbox/.

Run once. The PDF is the pipeline's real input: the parser does not import this
module, it extracts from the rendered text the way it would with a real report.

    cd apps/api && uv run python ../../scripts/generate_reports.py
"""

import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_JUSTIFY
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

sys.path.insert(0, str(Path(__file__).parent))
from synthetic_reports import MARCA, REPORTS

OUTPUT_DIR = Path(__file__).resolve().parents[1] / "data" / "reports" / "inbox"

AZUL = colors.HexColor("#0F3D5C")
CINZA = colors.HexColor("#5A6470")
CLARO = colors.HexColor("#EEF2F5")


def build_styles() -> dict:
    base = getSampleStyleSheet()
    return {
        "titulo": ParagraphStyle(
            "titulo", parent=base["Title"], fontSize=20, textColor=AZUL, spaceAfter=4
        ),
        "subtitulo": ParagraphStyle(
            "subtitulo", parent=base["Normal"], fontSize=10, textColor=CINZA, spaceAfter=18
        ),
        "secao": ParagraphStyle(
            "secao",
            parent=base["Heading1"],
            fontSize=14,
            textColor=AZUL,
            spaceBefore=16,
            spaceAfter=8,
        ),
        "sub": ParagraphStyle(
            "sub",
            parent=base["Heading2"],
            fontSize=11,
            textColor=AZUL,
            spaceBefore=12,
            spaceAfter=4,
        ),
        "corpo": ParagraphStyle(
            "corpo",
            parent=base["Normal"],
            fontSize=9.5,
            leading=14,
            alignment=TA_JUSTIFY,
            spaceAfter=6,
        ),
        "nota": ParagraphStyle(
            "nota", parent=base["Normal"], fontSize=8, textColor=CINZA, leading=11, spaceAfter=4
        ),
    }


def draw_frame(canvas, doc) -> None:
    """Stamps the synthetic-document marker and page number on every page."""
    canvas.saveState()
    canvas.setFont("Helvetica-Bold", 7)
    canvas.setFillColor(colors.HexColor("#B03A2E"))
    canvas.drawCentredString(A4[0] / 2, A4[1] - 1.1 * cm, MARCA)
    canvas.setFont("Helvetica", 8)
    canvas.setFillColor(CINZA)
    canvas.drawCentredString(A4[0] / 2, 1.2 * cm, f"Página {doc.page}")
    canvas.restoreState()


def table(data: list[list], widths: list[float], styles: dict) -> Table:
    wrapped = [
        [
            Paragraph(str(cell), styles["nota"])
            if i
            else Paragraph(f"<b>{cell}</b>", styles["nota"])
            for cell in row
        ]
        for i, row in enumerate(data)
    ]
    t = Table(wrapped, colWidths=widths, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), CLARO),
                ("TEXTCOLOR", (0, 0), (-1, 0), AZUL),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#D5DBE0")),
                ("LEFTPADDING", (0, 0), (-1, -1), 5),
                ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
        )
    )
    return t


def build_report(report: dict, styles: dict) -> list:
    story: list = []
    p = story.append

    p(Paragraph("Relatório de Análise Genômica", styles["titulo"]))
    p(Paragraph("Genera | Rede Dasa | Sequenciamento por microarray de SNPs", styles["subtitulo"]))

    p(
        table(
            [
                ["Campo", "Valor"],
                ["Identificação da amostra", report["patient_id"]],
                ["Nome", report["nome"]],
                ["Idade", f"{report['idade']} anos"],
                ["Sexo", report["sexo"]],
                ["Coleta", report["amostra"]],
                ["Emissão", report["emissao"]],
            ],
            [5.5 * cm, 10.5 * cm],
            styles,
        )
    )

    anc = report["ancestralidade"]
    p(Paragraph("1. Ancestralidade", styles["secao"]))
    p(Paragraph(anc["resumo"], styles["corpo"]))
    p(
        table(
            [["Região", "Proporção", "Detalhe"]] + [list(c) for c in anc["componentes"]],
            [6 * cm, 3 * cm, 7 * cm],
            styles,
        )
    )
    p(Spacer(1, 8))
    linhagens = [f"Haplogrupo materno: {anc['haplogrupo_materno']}"]
    if "haplogrupo_paterno" in anc:
        linhagens.append(f"Haplogrupo paterno: {anc['haplogrupo_paterno']}")
    linhagens.append(f"Componente neandertal: {anc['neandertal']}")
    for linha in linhagens:
        p(Paragraph(linha, styles["corpo"]))

    p(PageBreak())
    p(Paragraph("2. Predisposições a condições de saúde", styles["secao"]))
    p(
        Paragraph(
            "Predisposição genética não é diagnóstico. Os valores abaixo indicam "
            "probabilidade estatística em populações estudadas, e não previsão "
            "individual. Nenhum resultado deste relatório confirma ou exclui doença.",
            styles["corpo"],
        )
    )

    for item in report["predisposicoes"]:
        p(Paragraph(f"{item['condicao']} ({item['gene']})", styles["sub"]))
        p(
            table(
                [
                    ["Campo", "Valor"],
                    ["Gene", item["gene"]],
                    ["Variante", item["variante"]],
                    ["Genótipo", item["genotipo"]],
                    ["Classificação de risco", item["risco"]],
                    ["Risco relativo", item["risco_relativo"]],
                ],
                [5.5 * cm, 10.5 * cm],
                styles,
            )
        )
        p(Spacer(1, 6))
        p(
            Paragraph(
                f"<b>O que isso significa em números.</b> {item['risco_absoluto']}", styles["corpo"]
            )
        )
        p(Paragraph(f"<b>Interpretação.</b> {item['interpretacao']}", styles["corpo"]))
        p(Paragraph(f"<b>Encaminhamento.</b> {item['acao']}", styles["corpo"]))
        p(Paragraph(f"<b>Referência.</b> {item['fonte']}", styles["nota"]))
        p(Spacer(1, 4))

    p(PageBreak())
    p(Paragraph("3. Características e traços", styles["secao"]))
    p(
        Paragraph(
            "Achados sem implicação clínica, de caráter informativo.",
            styles["corpo"],
        )
    )
    p(
        table(
            [["Característica", "Gene", "Variante", "Resultado"]]
            + [list(t) for t in report["tracos"]],
            [4.5 * cm, 2.5 * cm, 4 * cm, 5 * cm],
            styles,
        )
    )

    p(Paragraph("4. Farmacogenética", styles["secao"]))
    p(
        Paragraph(
            "Informação destinada ao profissional de saúde. Nenhuma medicação deve ser "
            "iniciada, suspensa ou ajustada a partir deste relatório sem prescrição médica.",
            styles["corpo"],
        )
    )
    p(
        table(
            [["Fármaco", "Gene", "Genótipo", "Fenótipo", "Observação"]]
            + [list(f) for f in report["farmacogenetica"]],
            [2.8 * cm, 2 * cm, 2.2 * cm, 3.5 * cm, 5.5 * cm],
            styles,
        )
    )

    p(Paragraph("5. Metodologia e limitações", styles["secao"]))
    for texto in [
        (
            "A análise utiliza microarray de polimorfismos de nucleotídeo único (SNPs). "
            "A técnica cobre variantes específicas e não equivale a sequenciamento completo "
            "do genoma."
        ),
        (
            "Variantes raras ou não cobertas pelo painel não são detectadas. Resultado sem "
            "alteração não exclui a possibilidade da condição."
        ),
        (
            "As estimativas de risco derivam de estudos populacionais, predominantemente em "
            "populações europeias. A aplicabilidade a populações miscigenadas, como a "
            "brasileira, tem limitações reconhecidas na literatura."
        ),
        (
            "Este relatório tem finalidade informativa e educacional. Não constitui "
            "diagnóstico, prescrição ou prognóstico, e não substitui avaliação de "
            "profissional de saúde habilitado."
        ),
        (
            "A interpretação dos achados deve ser feita por médico ou geneticista, "
            "considerando histórico pessoal e familiar."
        ),
    ]:
        p(Paragraph(texto, styles["corpo"]))

    return story


def main() -> None:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    styles = build_styles()

    for report in REPORTS:
        path = OUTPUT_DIR / f"{report['patient_id']}.pdf"
        doc = SimpleDocTemplate(
            str(path),
            pagesize=A4,
            topMargin=1.8 * cm,
            bottomMargin=1.8 * cm,
            leftMargin=2.4 * cm,
            rightMargin=2.4 * cm,
            title=f"Relatório Genomico {report['patient_id']}",
        )
        doc.build(build_report(report, styles), onFirstPage=draw_frame, onLaterPages=draw_frame)
        print(f"gerado: {path.relative_to(OUTPUT_DIR.parents[2])}")


if __name__ == "__main__":
    main()
