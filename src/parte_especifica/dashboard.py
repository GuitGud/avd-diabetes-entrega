"""Painel da Parte Específica para exploração e apresentação."""
from pathlib import Path
import sys

import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

pasta = Path(__file__).resolve().parent
sys.path.insert(0, str(pasta))
from dados import (
    catalogar_colunas, descricao, faixas_de_peso, faixas_comparadas, formatar_taxas,
    identificadores, inteiro_pt, ler_base, ordem_idade, percentual_pt, quantitativas,
    rotulos, rotulos_desfecho, taxas_reinternacao,
)
from graficos import (
    grafico_caixas, grafico_duracoes, grafico_peso, grafico_qualidade, grafico_taxa_dia,
    grafico_taxa_idade,
)
from qualidade import auditar
from textos import FIGURAS, LIMITES, ORDEM_FIGURAS, PERGUNTA, RESPOSTA, TRATAMENTOS

st.set_page_config(page_title='Diabetes e reinternação | AVD', layout='wide')


@st.cache_data
def carregar():
    fonte = pasta.parents[1] / 'data/parte_especifica/diabetes_uci.zip'
    original, dados, mapas = ler_base(fonte)
    auditoria, contagens, exames = auditar(original, mapas)
    return original, dados, auditoria, contagens, exames, catalogar_colunas(original)


def exibir(figura):
    st.pyplot(figura)
    plt.close(figura)


def nota(chave, base_integral=True):
    ficha = FIGURAS[chave]
    st.caption(ficha['mostra'])
    with st.expander('Como ler este gráfico'):
        if base_integral:
            st.write(ficha['leitura'])
        st.write(ficha['escolha'])


def rotulo(coluna):
    return rotulos.get(coluna, coluna)


def reduzir_categorias(serie):
    valores = serie.astype(str)
    if valores.nunique() <= 12:
        return valores
    maiores = valores.value_counts().head(11).index
    return valores.where(valores.isin(maiores), 'Outras categorias')


original, dados, auditoria, contagens, exames, catalogo = carregar()
st.title('Diabetes e reinternação hospitalar')
st.write(PERGUNTA)

with st.sidebar:
    st.header('Recorte da análise')
    faixa = st.selectbox('Faixa etária', ['Todas', *ordem_idade], key='faixa_etaria')
    dias = st.slider('Permanência (dias)', 1, 14, (1, 14), key='permanencia')
    st.caption('Peso e auditoria usam a base original inteira.')

recorte = dados.loc[dados['time_in_hospital'].between(*dias)]
if faixa != 'Todas':
    recorte = recorte.loc[recorte['age'].eq(faixa)]
integral = len(recorte) == len(dados)

painel, explorar, qualidade = st.tabs(['Gráficos', 'Explorar duas variáveis', 'Dados e qualidade'])
with painel:
    st.header('Qualidade e peso')
    exibir(grafico_qualidade(contagens, exames))
    nota('q1')
    exibir(grafico_peso(faixas_de_peso(original), contagens['weight']))
    nota('peso')

    st.header('Permanência e reinternação')
    if recorte.empty:
        st.info('Nenhuma internação nesse recorte. Amplie a faixa de dias ou de idade.')
    else:
        um, dois = st.columns(2)
        um.metric('Internações no recorte', inteiro_pt(len(recorte)))
        dois.metric('Proporção registrada em menos de 30 dias', percentual_pt(recorte['readmitted'].eq('<30').mean()))
        exibir(grafico_duracoes(recorte['time_in_hospital'].value_counts().sort_index()))
        nota('permanencia', integral)
        duracoes_por_desfecho = {
            codigo: recorte.loc[recorte['readmitted'].eq(codigo), 'time_in_hospital']
            for codigo in rotulos_desfecho
            if recorte['readmitted'].eq(codigo).any()
        }
        exibir(grafico_caixas(duracoes_por_desfecho))
        nota('caixas', integral)

        taxas_dia = taxas_reinternacao(recorte, 'time_in_hospital')
        exibir(grafico_taxa_dia(taxas_dia))
        nota('reinternacao', integral)
        st.dataframe(formatar_taxas(taxas_dia).rename_axis('Dias').reset_index(), hide_index=True)
        st.download_button('Baixar tabela por duração', formatar_taxas(taxas_dia).to_csv().encode('utf-8-sig'),
                           'reinternacao_por_dia.csv', 'text/csv')

        idades = recorte.loc[recorte['age'].isin(faixas_comparadas)]
        if idades.empty:
            st.info('A comparação por idade usa as faixas de 60 a 69 e de 70 a 79 anos. Selecione uma dessas faixas ou todas as idades.')
        else:
            taxas_idade = taxas_reinternacao(idades, 'time_in_hospital', 'age')
            exibir(grafico_taxa_idade(taxas_idade))
            nota('idades', integral)
            tabela = formatar_taxas(taxas_idade).rename(index=faixas_comparadas, level='age')
            st.dataframe(tabela.rename_axis(index=['Dias', 'Faixa etária']).reset_index(), hide_index=True)

        if integral:
            st.subheader('O que observamos')
            st.write(RESPOSTA)
        st.caption(LIMITES)

with explorar:
    st.header('Compare duas colunas da base')
    colunas = [coluna for coluna in dados if coluna not in identificadores]
    x = st.selectbox('Primeira variável', colunas, index=colunas.index('time_in_hospital'),
                     format_func=rotulo, key='primeira_variavel')
    opcoes_y = [c for c in colunas if c != x]
    y = st.selectbox('Segunda variável', opcoes_y,
                     index=opcoes_y.index('num_medications') if 'num_medications' in opcoes_y else 0,
                     format_func=rotulo, key='segunda_variavel')
    st.write(f'**{x}** · {descricao[x]}')
    st.write(f'**{y}** · {descricao[y]}')
    pares = recorte[[x, y]].dropna()
    st.caption(f'{inteiro_pt(len(pares))} internações com os dois campos disponíveis de {inteiro_pt(len(recorte))} no recorte.')
    if pares.empty:
        st.info('Sem registros para comparar essas duas variáveis no recorte.')
    elif x in quantitativas and y in quantitativas:
        correlacao = pares[x].rank().corr(pares[y].rank()) if pares[x].nunique() > 1 and pares[y].nunique() > 1 else float('nan')
        if pd.notna(correlacao):
            st.write(f'**Correlação de Spearman** · {correlacao:.3f}'.replace('.', ','))
        else:
            st.info('A correlação precisa de variação nas duas colunas.')
        st.dataframe(pares.describe().round(2))
    elif x in quantitativas or y in quantitativas:
        medida, grupo = (x, y) if x in quantitativas else (y, x)
        pares = pares.assign(**{grupo: reduzir_categorias(pares[grupo])})
        resumo = pares.groupby(grupo, observed=True)[medida].agg(
            Registros='size', Mediana='median', Q1=lambda s: s.quantile(0.25), Q3=lambda s: s.quantile(0.75),
        )
        st.caption('Compare a mediana e os quartis da medida em cada categoria.')
        st.dataframe(resumo.rename_axis(rotulo(grupo)).reset_index(), hide_index=True)
    else:
        cruzamento = pd.crosstab(reduzir_categorias(pares[x]), reduzir_categorias(pares[y]))
        st.caption('A primeira tabela mostra contagens. A segunda usa o total de cada linha como denominador.')
        st.dataframe(cruzamento)
        st.dataframe(cruzamento.div(cruzamento.sum(axis=1), axis=0).mul(100).round(2).add_suffix(' (%)'))
    st.caption('Em tabelas com mais de 12 categorias, as menores são agrupadas como Outras categorias.')

with qualidade:
    st.header('Dados e qualidade')
    st.write(f'{inteiro_pt(len(original))} internações na base original e {inteiro_pt(len(dados))} na cópia de análise.')
    st.dataframe(auditoria, hide_index=True)
    for titulo, justificativa in TRATAMENTOS.items():
        st.markdown(f'**{titulo}** · {justificativa}')
    st.subheader('Dicionário de variáveis')
    for titulo, tabela in catalogo.items():
        with st.expander(titulo):
            escolha = st.selectbox('Atributo', tabela['Atributo'], key=titulo)
            st.write(descricao[escolha])
            st.dataframe(tabela[['Atributo', 'Tipo']], hide_index=True)
    notas = '\n\n'.join('\n'.join([FIGURAS[c]['titulo'], FIGURAS[c]['mostra'], FIGURAS[c]['leitura'], FIGURAS[c]['escolha']]) for c in ORDEM_FIGURAS)
    st.download_button('Baixar notas dos seis gráficos', notas.encode('utf-8'), 'notas_dos_graficos.txt', 'text/plain')
