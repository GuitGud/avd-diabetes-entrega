# [IA] Claude: converte docs/DECLARACAO_IA.md em docs/DECLARACAO_IA.pdf, com espaço para assinatura.
#
# Uso (da raiz do repositório):  python src/gerar_declaracao_pdf.py
# Suporta o Markdown usado na declaração: # e ## títulos, listas numeradas, parágrafos,
# **negrito**, `código` e a tabela de assinaturas.
import re
from pathlib import Path
from xml.sax.saxutils import escape

from matplotlib import font_manager
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

ROOT = Path(__file__).resolve().parents[1]
MD = ROOT / "docs" / "DECLARACAO_IA.md"
PDF = ROOT / "docs" / "DECLARACAO_IA.pdf"
AZUL = colors.HexColor("#17354b")


def inline(t):
    t = escape(t)
    t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
    return re.sub(r"`(.+?)`", r"<font face='Courier'>\1</font>", t)


def main():
    regular = font_manager.findfont("DejaVu Sans")
    bold = font_manager.findfont(font_manager.FontProperties(family="DejaVu Sans", weight="bold"))
    for nome, arq in [("AVD", regular), ("AVD-Bold", bold)]:
        if nome not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(nome, arq))
    pdfmetrics.registerFontFamily("AVD", normal="AVD", bold="AVD-Bold", italic="AVD", boldItalic="AVD-Bold")
    st = getSampleStyleSheet()
    for n in ["BodyText", "Title", "Heading2"]:
        st[n].fontName = "AVD" if n == "BodyText" else "AVD-Bold"
        st[n].textColor = AZUL
    st["BodyText"].fontSize = 9.5; st["BodyText"].leading = 13; st["BodyText"].spaceAfter = 4
    st["Title"].fontSize = 18; st["Title"].leading = 23
    st["Heading2"].fontSize = 12; st["Heading2"].spaceBefore = 10

    fl, tabela = [], []
    for linha in MD.read_text(encoding="utf-8").splitlines() + [""]:
        s = linha.strip()
        if s.startswith("|"):
            celulas = [c.strip() for c in s.strip("|").split("|")]
            if not all(set(c) <= set("-: ") for c in celulas):
                tabela.append(celulas)
            continue
        if tabela:  # fecha a tabela de assinaturas
            dados = [[Paragraph(inline(c), st["BodyText"]) for c in r] for r in tabela]
            t = Table(dados, colWidths=[200, 200, 80],
                      rowHeights=[None] + [34] * (len(dados) - 1), hAlign="LEFT")
            t.setStyle(TableStyle([
                ("GRID", (0, 0), (-1, -1), .5, colors.HexColor("#8198a8")),
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#deebf1")),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE")]))
            fl.extend([t, Spacer(1, 8)])
            tabela = []
        if not s:
            continue
        if s.startswith("# "):
            fl.append(Paragraph(inline(s[2:]), st["Title"]))
        elif s.startswith("## "):
            fl.append(Paragraph(inline(s[3:]), st["Heading2"]))
        else:
            fl.append(Paragraph(inline(s), st["BodyText"]))

    SimpleDocTemplate(str(PDF), pagesize=(595.28, 841.89), leftMargin=56, rightMargin=56,
                      topMargin=40, bottomMargin=40, title="Declaração de Uso de IA").build(fl)
    print("ok:", PDF)


if __name__ == "__main__":
    main()
