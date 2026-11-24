# Diabetes e reinternação hospitalar

Parte Específica do projeto de Análise e Visualização de Dados.

**Pergunta de pesquisa** · Como a proporção de reinternações registradas em menos de 30 dias varia conforme a duração da internação?

## Colab

Abra `Dashboard_Diabetes_Colab.ipynb` no Colab, conecte o ambiente e escolha **Ambiente de execução → Executar tudo**. O arquivo contém a base e o código. A última célula inicia o Streamlit. Rode até a conclusão para ver o painel.

## Painel no computador

Extraia o pacote. No terminal, entre na pasta `projeto-avd` e rode os comandos com Python 3.11 ou superior.

```bash
python -m pip install -r requirements.txt
python -m streamlit run src/parte_especifica/dashboard.py
```

A aba **Gráficos** mostra as seis figuras. Os filtros de idade e permanência recalculam os gráficos de permanência e desfecho. A aba **Explorar duas variáveis** permite escolher um par e conferir seus totais. Na aba **Dados e qualidade** ficam as verificações e o dicionário das colunas.

## Arquivos do trabalho

| Arquivo ou pasta | Conteúdo |
| --- | --- |
| `relatorio.pdf` | Análise, resposta à pergunta e dicionário dos 50 atributos. |
| `Guia_Defesa_Professora.pdf` | Fala, justificativa e números de cada gráfico. Inclui exemplos para perguntas sobre pares de variáveis. |
| `explicacao.md` | Onde encontrar os itens da avaliação e o que o código faz. |
| `out/parte_especifica/` | Tabelas e gráficos da análise. |
| `DATA_SOURCE.md` | Referência e licença da base. |
