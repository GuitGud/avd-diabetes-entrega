# Projeto AVD: Análise e Visualização de Dados

**Integrantes:** William de Souza Bezerra, Mariana Medeiros de Barros Correia, Guilherme Alcoforado Rabelo, Tomás de Aquino Vieira Jamacaru

O projeto tem duas partes:

| Parte | Dataset | Conteúdo |
|---|---|---|
| **Parte Comum** | Obesity (UCI, id 544) | EDA dos 4 pilares, padronização, K-Means em duas passadas (Método do Cotovelo e k igual ao número de classes), matriz de confusão, acurácia, precisão e recall por classe, e discussão crítica |
| **Parte Específica** | Diabetes 130-US Hospitals (1999-2008) | EDA, storytelling, 4 visualizações exploratórias e 2 explanatórias, e dashboard em Streamlit sobre reinternação em menos de 30 dias |

**Pergunta de pesquisa da Parte Específica:** quanto mais vezes o paciente foi internado no ano anterior, e quanto mais vezes foi à emergência, maior a chance de voltar ao hospital em menos de 30 dias?

## Estrutura do repositório

```
.
├── README.md
├── requirements.txt
├── relatorio.pdf                      # relatório das duas partes
├── docs/
│   ├── DECLARACAO_IA.pdf              # declaração assinada por todos
│   └── MATRIZ_CONTRIBUICAO.md
├── data/
│   ├── parte_comum/                   # ObesityDataSet_raw_and_data_sinthetic.csv
│   └── parte_especifica/              # diabetic_data.csv, IDS_mapping.csv, DATA_SOURCE.md
├── notebooks/
│   ├── parte_comum/                   # parte_comum_obesity.ipynb (EDA + K-Means)
│   └── parte_especifica/              # notebook Colab da Parte Específica
├── out/
│   ├── parte_comum/                   # tabelas e figuras geradas pela Parte Comum
│   └── parte_especifica/              # tabelas, figuras e notas geradas pela Parte Específica
└── src/
    ├── gerar_declaracao_pdf.py        # gera docs/DECLARACAO_IA.pdf a partir do .md
    ├── parte_comum/
    │   └── relatorio_pdf.py           # gera o relatório da Parte Comum e monta o relatorio.pdf final
    └── parte_especifica/
        ├── analise.py                 # leitura, auditoria, ausências, outliers, relações
        ├── figuras.py                 # figuras estáticas
        ├── documentos.py              # relatório PDF/Markdown
        ├── textos_grupo.py            # textos analíticos
        └── dashboard.py               # dashboard Streamlit
```

## Como executar

Requer Python 3.11 ou superior.

```bash
python -m pip install -r requirements.txt
```

**Dashboard (Parte Específica):**

```bash
python -m streamlit run src/parte_especifica/dashboard.py
```

**Parte Comum:** abra `notebooks/parte_comum/parte_comum_obesity.ipynb` no Jupyter, no VS Code ou no Colab e execute todas as células. As tabelas e figuras vão para `out/parte_comum/`. No Colab sem o repositório, o notebook baixa o CSV direto da UCI.

**Relatório PDF (as duas partes):**

```bash
python src/parte_especifica/documentos.py   # gera out/parte_especifica/relatorio_parte_especifica.pdf
python src/parte_comum/relatorio_pdf.py     # gera a Parte Comum e junta tudo em relatorio.pdf
```

**Parte Específica no Colab:** abra `notebooks/parte_especifica/Dashboard_Diabetes_Colab.ipynb` e use *Ambiente de execução → Executar tudo*. O notebook traz os dados embutidos e abre o dashboard na última célula.

## Bibliotecas

A análise usa apenas as bibliotecas permitidas: pandas, numpy, matplotlib, seaborn, plotly, scikit-learn e streamlit. O `requirements.txt` inclui mais três, que **não participam da análise**:

- `reportlab` e `pypdf`: só geram e juntam os PDFs (`relatorio.pdf` e `docs/DECLARACAO_IA.pdf`);
- `jupyter`: só executa os notebooks localmente (no Colab já vem instalado).

## Uso de IA

O uso de IA está descrito em [docs/DECLARACAO_IA.pdf](docs/DECLARACAO_IA.pdf). O PDF é gerado a partir de `docs/DECLARACAO_IA.md` com `python src/gerar_declaracao_pdf.py`. Os trechos de código gerados com IA estão marcados com `# [IA] Claude`.

## Fontes dos dados

- Clore, J.; Cios, K.; DeShazo, J.; Strack, B. (2014). *Diabetes 130-US Hospitals for Years 1999-2008*. UCI Machine Learning Repository. https://doi.org/10.24432/C5230J (CC BY 4.0)
- Palechor, F. M.; De la Hoz Manotas, A. (2019). *Dataset for estimation of obesity levels based on eating habits and physical condition in individuals from Colombia, Peru and Mexico*. Data in Brief, 25, 104344. https://doi.org/10.1016/j.dib.2019.104344. Dados: UCI Machine Learning Repository, id 544 (CC BY 4.0)


Matriz de Contribuição:
Tomás: Parte Comum do projeto e Revisar erros

