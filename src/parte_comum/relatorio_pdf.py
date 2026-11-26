# [IA] Claude: gera o relatório da Parte Comum e monta o relatorio.pdf final (Parte Comum + Parte Específica).
#
# Uso (da raiz do repositório, depois de executar notebooks/parte_comum/parte_comum_obesity.ipynb):
#     python src/parte_comum/relatorio_pdf.py
#
# Entradas: out/parte_comum/*.csv e out/parte_comum/figuras/*.png
#           out/parte_especifica/relatorio_parte_especifica.pdf (gerado por src/parte_especifica/documentos.py)
# Saídas:   out/parte_comum/relatorio_parte_comum.pdf e relatorio.pdf (raiz)
from pathlib import Path
from xml.sax.saxutils import escape

import pandas as pd
from matplotlib import font_manager
from pypdf import PdfWriter
from reportlab.lib import colors
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (Image, PageBreak, Paragraph, SimpleDocTemplate, Spacer, Table,
                                TableStyle)

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "out" / "parte_comum"
FIG = OUT / "figuras"
PDF_COMUM = OUT / "relatorio_parte_comum.pdf"
PDF_ESPECIFICA = ROOT / "out" / "parte_especifica" / "relatorio_parte_especifica.pdf"
PDF_FINAL = ROOT / "relatorio.pdf"
AZUL = colors.HexColor("#17354b")
LARG = 499


def pct(v):
    return f"{v * 100:.1f}%".replace(".", ",")


def estilos():
    regular = font_manager.findfont("DejaVu Sans")
    bold = font_manager.findfont(font_manager.FontProperties(family="DejaVu Sans", weight="bold"))
    for nome, arq in [("AVD", regular), ("AVD-Bold", bold)]:
        if nome not in pdfmetrics.getRegisteredFontNames():
            pdfmetrics.registerFont(TTFont(nome, arq))
    pdfmetrics.registerFontFamily("AVD", normal="AVD", bold="AVD-Bold", italic="AVD", boldItalic="AVD-Bold")
    st = getSampleStyleSheet()
    for n in ["Normal", "BodyText", "Title", "Heading1", "Heading2"]:
        st[n].fontName = "AVD" if n in ("Normal", "BodyText") else "AVD-Bold"
        st[n].textColor = AZUL
    st["BodyText"].fontSize = 9; st["BodyText"].leading = 13; st["BodyText"].spaceAfter = 7
    st["Title"].fontSize = 25; st["Title"].leading = 31
    st["Heading1"].fontSize = 16; st["Heading1"].leading = 21; st["Heading1"].spaceBefore = 10
    st["Heading2"].fontSize = 12; st["Heading2"].leading = 16
    st["Heading1"].keepWithNext = True; st["Heading2"].keepWithNext = True
    st.add(ParagraphStyle("Tab", fontName="AVD", fontSize=7, leading=9, textColor=AZUL))
    return st


def construir_parte_comum():
    st = estilos()
    fl = []

    def p(txt, kind="BodyText"):
        # **negrito** simples -> <b>
        t = escape(txt)
        while "**" in t:
            t = t.replace("**", "<b>", 1).replace("**", "</b>", 1)
        fl.append(Paragraph(t, st[kind]))

    def h(txt):
        p(txt, "Heading1")

    def bullets(itens):
        for it in itens:
            p("• " + it)

    def tabela(df, larguras=None):
        dados = [[Paragraph(escape(str(c)), st["Tab"]) for c in df.columns]]
        for row in df.itertuples(index=False, name=None):
            dados.append([Paragraph(escape(f"{v:.3f}" if isinstance(v, float) else str(v)), st["Tab"])
                          for v in row])
        t = Table(dados, colWidths=larguras or [LARG / len(df.columns)] * len(df.columns),
                  repeatRows=1, hAlign="LEFT")
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#deebf1")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#f4f7f9")]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LINEBELOW", (0, 0), (-1, 0), .5, colors.HexColor("#8198a8"))]))
        fl.extend([t, Spacer(1, 10)])

    def figura(nome, max_h=300):
        from PIL import Image as PILImage
        caminho = FIG / nome
        with PILImage.open(caminho) as im:
            w, hh = im.size
        esc = min(LARG / w, max_h / hh)
        fl.extend([Image(str(caminho), width=w * esc, height=hh * esc), Spacer(1, 6)])

    ler = lambda n, **kw: pd.read_csv(OUT / n, **kw)
    cot = ler("cotovelo.csv")
    comp = ler("comparacao_passadas.csv", index_col=0)
    m1 = ler("passada1_metricas.csv", index_col=0)
    m2 = ler("passada2_metricas.csv", index_col=0)
    ext = ler("analise_complementar_atributos.csv", index_col=0)
    imc = ler("imc_por_classe.csv")
    outl = ler("outliers_iqr.csv", index_col=0)
    k1 = int(comp.loc["k", "Passada 1 (cotovelo)"])
    acc1 = comp.loc["acurácia", "Passada 1 (cotovelo)"]
    acc2 = comp.loc["acurácia", "Passada 2 (k = 7)"]

    # ---------- capa do relatório completo ----------
    p("PROJETO AVD / RELATÓRIO", "Heading2")
    p("Parte Comum e Parte Específica", "Title")
    p("Integrantes: William de Souza Bezerra, Mariana Medeiros de Barros Correia, Guilherme Alcoforado Rabelo, Tomás de Aquino Vieira Jamacaru")
    p("Data de entrega: 26/11/2026")
    fl.append(Spacer(1, 14))
    p("Conteúdo", "Heading2")
    bullets([
        "**Parte Comum (4,0 pontos)**: K-Means no dataset Obesity, com EDA dos 4 pilares, padronização, "
        "duas passadas de K-Means, matrizes de confusão, métricas e discussão crítica. Vem logo após esta capa, "
        "com rodapé \"Parte Comum\".",
        "**Parte Específica (6,0 pontos)**: Diabetes 130-US Hospitals, com EDA, storytelling, visualizações e "
        "dashboard Streamlit. Vem na sequência, com rodapé e numeração próprios (\"Parte Específica\").",
    ])
    p("O código, os dados e as tabelas de evidência estão no repositório GitHub, nas pastas notebooks/, src/, "
      "data/ e out/. O uso de IA está declarado em docs/DECLARACAO_IA.pdf.")
    fl.append(PageBreak())

    # ---------- Parte Comum ----------
    p("PARTE COMUM", "Heading2")
    p("K-Means no dataset Obesity", "Title")
    p("Fonte: Palechor & De la Hoz Manotas (2019), Estimation of obesity levels based on eating habits and "
      "physical condition, UCI Machine Learning Repository, id 544. Notebook: "
      "notebooks/parte_comum/parte_comum_obesity.ipynb.")

    h("1. Estrutura")
    bullets([
        "2.111 registros e 17 atributos: 8 numéricos e 9 categóricos, incluindo o alvo NObeyesdad com 7 classes. "
        "**Não há valores ausentes.**",
        "**24 linhas duplicadas** foram removidas, porque contariam duas vezes nos centróides. Restam 2.087.",
        "Segundo os autores, **77% dos registros são sintéticos (SMOTE)**. Por isso as respostas ordinais "
        "(FCVC, NCP, CH2O, FAF e TUE) aparecem com casas decimais, e as classes são quase balanceadas.",
        "O rótulo é definido pelas **faixas de IMC** (peso / altura²) da OMS.",
    ])

    h("2. Distribuições")
    figura("C2_histogramas.png", 260)
    bullets([
        "A idade é assimétrica à direita: a maioria tem de 18 a 26 anos, e a cauda vai até 61.",
        "O peso tem uma faixa larga, de 39 a 173 kg, com vários picos. A altura é quase simétrica.",
        "As ordinais concentram valores nos inteiros, com decimais entre eles (efeito do SMOTE). SMOKE e SCC "
        "são raras, com menos de 5% de \"yes\". Em MTRANS, 75% usam transporte público e 22% automóvel.",
    ])

    h("3. Relações")
    figura("C5_altura_peso_imc.png", 230)
    tabela(imc.rename(columns={"NObeyesdad": "classe", "min": "IMC mín.", "median": "IMC mediano",
                               "max": "IMC máx."}), [190, 103, 103, 103])
    bullets([
        "O peso é a variável mais associada ao IMC (ρ de Spearman = 0,93). Os hábitos têm correlação fraca "
        "com o IMC, abaixo de 0,3 em módulo.",
        "As classes aparecem como faixas diagonais no gráfico altura × peso e **se sobrepõem entre vizinhas**. "
        "Overweight I e II dividem a faixa de 25,7 a 28,8, e Obesity II e III a de 36,8 a 39,8.",
        "Obesity_Type_II é 99% masculina e Obesity_Type_III, 99,7% feminina: um viés da amostra.",
    ])

    h("4. Outliers")
    o = outl.reset_index().rename(columns={"index": "variável"})
    tabela(o, [120, 95, 95, 95, 94])
    p("Os outliers do IQR se concentram em Age, com 8% acima de cerca de 35 anos, e em NCP, que fica quase sempre "
      "em 3. Todos os valores são plausíveis, sem erro de medida, por isso a **decisão foi mantê-los**. Removê-los "
      "apagaria grupos reais, e a padronização limita o peso de cada ponto.")

    h("5. Pré-processamento e padronização")
    bullets([
        "Binárias viram 0 ou 1, CAEC e CALC viram ordinais de 0 a 3 e MTRANS passa por one-hot, num total de "
        "20 atributos. O alvo e o IMC ficam de fora, porque o K-Means é não supervisionado.",
        "**Por que padronizar:** o K-Means usa distância euclidiana. Sem padronização, a variável de maior "
        "amplitude domina. O desvio do peso (≈ 26 kg) é cerca de 280 vezes o da altura (≈ 0,09 m), e o "
        "agrupamento seria praticamente só pelo peso. O StandardScaler leva cada coluna para média 0 e "
        "desvio 1.",
    ])

    fl.append(PageBreak())
    h(f"6. Passada 1: k livre (2 a 10), Método do Cotovelo → k = {k1}")
    figura("C8_cotovelo.png", 230)
    p("A inércia cai de forma quase linear, sem uma dobra nítida. Pelo critério da maior distância até a reta "
      f"entre k=2 e k=10, o cotovelo fica em **k = {k1}**, empatado com k = 6, e escolhemos o menor. A silhueta, "
      "sempre abaixo de 0,25, mostra clusters pouco compactos: os dados não têm grupos naturais bem separados.")
    figura("passada1_matriz_confusao.png", 290)
    tabela(m1.reset_index().rename(columns={"index": "classe"}), [150, 80, 80, 80, 109])

    fl.append(PageBreak())
    h("7. Passada 2: k = 7, o número real de classes")
    figura("passada2_matriz_confusao.png", 290)
    tabela(m2.reset_index().rename(columns={"index": "classe"}), [150, 80, 80, 80, 109])
    p("Cada cluster recebe a classe majoritária dos seus membros. Quando dois clusters têm a mesma classe "
      "majoritária, alguma classe deixa de ser prevista: a precisão dela fica registrada como 0 e o recall é 0.")

    h("8. Comparação das passadas")
    tabela(comp.reset_index().rename(columns={"index": "métrica"}), [200, 150, 149])
    figura("C9_recall_passadas.png", 220)

    p("Visualização dos clusters (PCA em 2D)", "Heading2")
    figura("C10_clusters_pca.png", 200)
    bullets([
        "**O plano tem duas massas, e elas não são as classes.** A faixa de cima reúne quem usa transporte "
        "público, e a nuvem de baixo, quem usa automóvel (pessoas mais velhas, média de 32 anos). O K-Means "
        "captura essa divisão primeiro: o cluster do automóvel mistura todas as classes de peso.",
        "**Dentro de cada massa, as classes formam um gradiente ordenado,** de Insufficient a Obesity III, sem "
        "fronteiras. É a imagem de um contínuo (IMC), e não de grupos separados.",
        "**Na passada 2, três clusters são minúsculos** (a pé, moto e bicicleta). O K-Means gastou 3 dos 7 "
        "clusters em categorias raras de transporte.",
        "Os dois componentes explicam só 25,4% da variância, mas a baixa pureza dos clusters, medida nas 20 "
        "dimensões, confirma a mistura.",
    ])

    h("9. Análise complementar (k = 7)")
    tabela(ext.reset_index().rename(columns={"index": "atributos usados"}), [200, 150, 149])

    fl.append(PageBreak())
    h("10. Discussão crítica")
    p("Texto redigido com apoio de IA (Claude) a partir dos resultados. O grupo revisou e se responsabiliza.")
    p("Comparação das passadas", "Heading2")
    bullets([
        f"Passada 1 (k = {k1}): acurácia de {pct(acc1)}. Com só {k1} clusters, 3 das 7 classes nunca são previstas.",
        f"Passada 2 (k = 7): acurácia de {pct(acc2)}, sem melhora. **Overweight I e II continuam sem cluster "
        "próprio.** A pureza sobe pouco (de 0,375 para 0,416) e a silhueta cai (de 0,191 para 0,132).",
    ])
    p("O que os clusters realmente separam", "Heading2")
    bullets([
        "Na passada 2, três clusters são definidos pelo **meio de transporte**: a pé (55 pessoas), moto (11) e "
        "bicicleta (7). O cluster de automóvel reúne as pessoas mais velhas, com média de 32 anos contra cerca de 22.",
        "Esse é um efeito da padronização sobre dummies raras: MTRANS_Bike vale 1 em 0,3% das linhas e, "
        "padronizada, vira z ≈ 17. Para o K-Means, andar de bicicleta pesa mais do que qualquer diferença de peso.",
        "Os 20 atributos entram com peso igual, mas só altura e peso definem o rótulo.",
    ])
    p("As classes originais fazem sentido? Sobrepeso × Obesidade I", "Heading2")
    bullets([
        "**Clinicamente, sim.** São faixas da OMS (IMC de 25 a 29,9 e de 30 a 34,9) com riscos diferentes.",
        "**Como grupos naturais nos dados, não.** São cortes arbitrários num contínuo: IMC 29,8 e 30,1 são "
        "quase idênticos em todos os atributos, mas ficam em classes diferentes. Não existe uma lacuna de "
        "densidade que o K-Means possa encontrar.",
        "Neste dataset, a fronteira é ainda mais borrada, porque o SMOTE interpola pontos entre classes vizinhas. "
        "Por isso Sobrepeso I e II nunca são majoritárias em nenhum cluster: ficam espremidas entre Normal "
        "e Obesidade I.",
        "Os dados sustentam no máximo 3 ou 4 grupos amplos (abaixo do peso ou normal, sobrepeso, obesidade e "
        "obesidade grave), o que coincide com o cotovelo em k = 4.",
    ])
    p("Análise complementar", "Heading2")
    p(f"Com k = 7, a acurácia muda conforme os atributos usados: só altura e peso, "
      f"{pct(ext.loc['altura_peso', 'acurácia'])}; só o IMC, {pct(ext.loc['so_imc', 'acurácia'])}; sem altura "
      f"e peso, {pct(ext.loc['sem_altura_peso', 'acurácia'])}. **A informação que separa as classes está no "
      "IMC, não nos hábitos.**")
    p("Limitações", "Heading2")
    bullets([
        "O K-Means supõe clusters esféricos e de tamanho parecido. A distância euclidiana sobre dados mistos é "
        "uma aproximação, e K-Prototypes ou o agrupamento das categorias raras de MTRANS seriam melhorias.",
        "Os resultados dependem da semente (random_state = 42, n_init = 10). Os dados são majoritariamente "
        "sintéticos.",
    ])
    p("Conclusão", "Heading2")
    p("O K-Means não recupera as 7 classes, nem com k = 7. Isso não é falha do algoritmo: as classes são "
      "cortes de um contínuo (IMC), e não grupos naturais. Sobrepeso e Obesidade I são úteis clinicamente, "
      "mas não aparecem como grupos distintos nos dados.")

    def rodape(c, doc):
        c.setFont("AVD", 8); c.setFillColor(colors.HexColor("#627d90"))
        c.drawString(48, 25, "Projeto AVD | Obesity | Parte Comum" if doc.page > 1 else "Projeto AVD")
        c.drawRightString(547, 25, str(doc.page))

    doc = SimpleDocTemplate(str(PDF_COMUM), pagesize=(595.28, 841.89), rightMargin=48, leftMargin=48,
                            topMargin=42, bottomMargin=45, title="Projeto AVD - Relatório",
                            author="Projeto AVD")
    doc.build(fl, onFirstPage=rodape, onLaterPages=rodape)


def juntar():
    w = PdfWriter()
    for pdf in [PDF_COMUM, PDF_ESPECIFICA]:
        w.append(str(pdf))
    w.add_metadata({"/Title": "Projeto AVD - Relatório (Parte Comum e Parte Específica)"})
    with open(PDF_FINAL, "wb") as f:
        w.write(f)


if __name__ == "__main__":
    construir_parte_comum()
    juntar()
    print("ok:", PDF_FINAL)
