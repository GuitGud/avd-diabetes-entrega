"""Dashboard da Parte Específica - EDA, narrativa, qualidade e rastreabilidade."""
from pathlib import Path
import hashlib
import json
import sys
import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st

sys.path.insert(0,str(Path(__file__).resolve().parent))
from analise import ROOT, AGE_ORDER, NUMERIC, LABELS, ORDER, COLORS, GROUPS, read_data, prepare, run_analysis, rate_by, strata_table, chart_notes
# [IA] Claude – novas tabelas e gráficos usados no painel
from analise import CORES_BINARIAS, TIPOS_FALTANTE, PARES_AUSENCIA, TEXTO_GRUPO, format_pct, audit_positive, missing_crosstab, binary_class, correlations_by_class, kde_counts, ecdf_table
from documentos import STORY_TITULOS, story_text
import textos_grupo as TG

st.set_page_config(page_title='Diabetes | Projeto AVD',page_icon='📊',layout='wide')
st.markdown('''<style>.block-container{padding-top:2rem;max-width:1450px}h1,h2,h3{letter-spacing:-.02em}
[data-testid="stMetric"]{background:#edf4f7;border-radius:12px;padding:16px}
[data-testid="stMetricLabel"],[data-testid="stMetricValue"]{color:#17354b}</style>''',unsafe_allow_html=True)

@st.cache_data
def load_all():
    return run_analysis(ROOT)

raw,base,tables,summary=load_all()
st.caption('PROJETO AVD · PARTE ESPECÍFICA · 1999-2008')
st.title('Diabetes e reinternação hospitalar')
st.write('Da exploração à comunicação: histórico de atendimento, qualidade dos registros e reinternação em menos de 30 dias.')
# [IA] Claude – informa a opção escolhida no notebook para as linhas NO
st.caption('Linhas readmitted = NO: '+{None:'escolha pendente (mantidas até o grupo decidir)',True:'removidas',False:'mantidas'}[summary['remover_no']])
with st.sidebar:
    st.header('Recorte da análise')
    ages=st.multiselect('Faixa etária',AGE_ORDER,default=AGE_ORDER)
    sexes=st.multiselect('Sexo',sorted(base.sexo.unique()),default=sorted(base.sexo.unique()))
    insulin=st.multiselect('Uso de insulina',sorted(base.insulin.unique()),default=sorted(base.insulin.unique()))
    days=st.slider('Permanência hospitalar (dias)',1,14,(1,14))
    one_per_patient=st.checkbox('Uma internação por paciente',help='Seleciona o menor encounter_id antes dos filtros; o identificador não é uma data confirmada.')
    exclude_terminal=st.checkbox('Excluir altas por óbito/hospice',help='Sensibilidade de denominador: códigos 11, 13, 14, 19, 20 e 21 do dicionário original.')
    st.caption('Os seis gráficos principais, a narrativa e as notas acompanham estes filtros. A auditoria de qualidade usa a base integral.')
cohort=base.sort_values('encounter_id').drop_duplicates('patient_nbr') if one_per_patient else base
if exclude_terminal:cohort=cohort.loc[~cohort.discharge_disposition_id.isin([11,13,14,19,20,21])]
filtered=cohort.loc[cohort.age.isin(ages)&cohort.sexo.isin(sexes)&cohort.insulin.isin(insulin)&cohort.time_in_hospital.between(*days)].copy()
if filtered.empty:
    st.info('Nenhuma internação atende aos filtros. Amplie as categorias selecionadas na lateral.');st.stop()
filter_description={'idades':ages,'sexo':sexes,'insulina':insulin,'dias':days,'uma_internacao_por_paciente':one_per_patient,'excluir_obito_hospice':exclude_terminal}
signature=hashlib.sha256(json.dumps(filter_description,sort_keys=True).encode()).hexdigest()[:10]
notes=chart_notes(filtered)
metrics=st.columns(4)
for col,label,value in zip(metrics,['Internações no recorte','Pacientes distintos','Reinternação <30 dias','Permanência média'],[f'{len(filtered):,}'.replace(',','.'),f'{filtered.patient_nbr.nunique():,}'.replace(',','.'),f'{filtered.reinternacao_30.mean():.1%}'.replace('.',','),f'{filtered.time_in_hospital.mean():.1f} dias'.replace('.',',')]):col.metric(label,value)


# [IA] Claude – título da legenda configurável
def show_chart(fig,key,legend='Reinternação'):
    fig.update_layout(template='plotly_white',legend_title_text=legend,margin=dict(l=20,r=20,t=90,b=55),height=fig.layout.height or 420)
    st.plotly_chart(fig,width='stretch',key=key)


# [IA] Claude – histograma em subplots por desfecho, com contagens no eixo y
def hist_by_outcome(variable,title):
    t=filtered.groupby(['desfecho',variable],observed=True).size().reset_index(name='internacoes')
    fig=px.bar(t,x=variable,y='internacoes',color='desfecho',facet_col='desfecho',title=title,category_orders={'desfecho':[o for o in ORDER if t.desfecho.eq(o).any()]},color_discrete_map=COLORS,labels={variable:LABELS[variable],'internacoes':'Contagem de registros','desfecho':'Reinternação'})
    fig.for_each_annotation(lambda a:a.update(text=a.text.split('=')[-1]));fig.update_layout(bargap=.2);fig.update_yaxes(matches=None,showticklabels=True)
    return fig


def show_note(key):
    n=notes[key]
    with st.expander(f'Nota analítica {key} - {n["titulo"]}'):
        st.markdown(f'**O que mostra:** {n["o_que_mostra"]}\n\n**Interpretação:** {n["interpretacao"]}\n\n**Escolha visual:** {n["escolha_visual"]}')


def heatmap(a,b,key):
    t=strata_table(filtered,a,b)
    vals=t.pivot(index=a,columns=b,values='percentual').reindex(index=AGE_ORDER if a=='age' else GROUPS,columns=GROUPS)
    ns=t.pivot(index=a,columns=b,values='n').reindex_like(vals)
    fig=px.imshow(vals,color_continuous_scale='YlOrRd',zmin=0,zmax=100,aspect='auto',title=notes[key]['titulo'],
                  labels={'x':'Internações prévias' if b=='grupo_internacoes' else 'Emergências prévias','y':'Faixa etária' if a=='age' else 'Internações prévias','color':'<30 dias (%)'})
    custom=np.stack([ns.to_numpy(),vals.to_numpy()],axis=-1)
    fig.update_traces(customdata=custom,hovertemplate='%{y} × %{x}<br>Proporção: %{z:.2f}%<br>Internações: %{customdata[0]:.0f}<extra></extra>')
    show_chart(fig,key);show_note(key)
    st.dataframe(t,hide_index=True)

eda,story,quality,notebook_docs,model=st.tabs(['1 · Exploração','2 · Pergunta e narrativa','3 · Qualidade','4 · Notas e catálogo','5 · Classificação'])
with eda:
    structural,distributions,relations=st.tabs(['Estrutura e tipos','Distribuições','Relações multivariadas'])
    with structural:
        # [IA] Claude – tabelas separadas de atributos e estatísticas numéricas
        st.subheader('Estrutura e tipos dos 50 atributos')
        st.write(f'Base integral: {len(raw):,} internações, {raw.patient_nbr.nunique():,} pacientes e {raw.shape[1]} colunas originais.')
        st.caption('Códigos de admissão e alta são categorias nominais, mesmo quando o CSV os armazena como inteiros. Idade e peso são intervalos; IDs não são medidas quantitativas.')
        larga={'descricao':st.column_config.TextColumn('descricao',width='large')}
        st.markdown('**Atributos qualitativos**');st.dataframe(tables['estrutura_qualitativos'],hide_index=True,column_config=larga)
        st.markdown('**Atributos quantitativos**');st.dataframe(tables['estrutura_quantitativos'],hide_index=True,column_config=larga)
        st.markdown('**Estatísticas das variáveis numéricas**');st.dataframe(tables['estatisticas_numericas'],hide_index=True)
        st.download_button('Baixar dicionário de atributos',tables['estrutura_atributos'].to_csv(index=False).encode('utf-8-sig'),'estrutura_atributos.csv','text/csv')
    with distributions:
        a,b=st.columns(2)
        with a:
            # [IA] Claude – E1 com duas cores
            counts=filtered.assign(classe=binary_class(filtered)).groupby(['age','classe'],observed=True).size().reset_index(name='internacoes')
            fig=px.bar(counts,x='age',y='internacoes',color='classe',barmode='stack',title='E1 · Internações por faixa etária',category_orders={'age':AGE_ORDER,'classe':list(CORES_BINARIAS)},color_discrete_map=CORES_BINARIAS,labels={'age':'Faixa etária (anos)','internacoes':'Internações','classe':'Reinternação'})
            show_chart(fig,'E1');show_note('E1')
        with b:
            fig=px.box(filtered,x='desfecho',y='time_in_hospital',color='desfecho',points=False,title='E2 · Permanência por desfecho',category_orders={'desfecho':ORDER},color_discrete_map=COLORS,labels={'desfecho':'Reinternação','time_in_hospital':'Permanência (dias)'})
            show_chart(fig,'E2');show_note('E2')
        # [IA] Claude – E3 em subplots por desfecho, barras espaçadas e KDE em vermelho
        fig=hist_by_outcome('num_medications','E3 · Medicamentos por internação, por desfecho')
        presentes=[o for o in ORDER if filtered.desfecho.eq(o).any()];mostrar=True
        for i,o in enumerate(presentes,1):
            curve=kde_counts(filtered.loc[filtered.desfecho.eq(o),'num_medications'])
            if curve is not None:
                fig.add_scatter(x=curve[0],y=curve[1],mode='lines',line=dict(color='red',width=2),name='Densidade (KDE, escala de contagem)',legendgroup='kde',showlegend=mostrar,row=1,col=i);mostrar=False
        show_chart(fig,'E3');show_note('E3')
        st.subheader('Distribuições de todos os atributos analíticos')
        chosen=st.selectbox('Atributo para distribuição',[c for c in raw if c not in ['encounter_id','patient_nbr']])
        if chosen in NUMERIC:
            # [IA] Claude – histogramas por desfecho e ECDF da variável numérica escolhida
            show_chart(hist_by_outcome(chosen,f'Distribuição de {chosen} por desfecho'),'dist_all');show_note('H1' if chosen in NUMERIC[:4] else 'H2')
            fig=px.line(ecdf_table(filtered[chosen]),x='valor',y='acumulada',line_shape='hv',markers=True,title=f'Distribuição acumulada (ECDF) de {chosen}',labels={'valor':LABELS[chosen],'acumulada':'Proporção acumulada'})
            fig.update_traces(name='ECDF',showlegend=True);fig.update_yaxes(range=[0,1.03]);show_chart(fig,'ecdf_all','Curva');show_note('A1')
        else:
            # [IA] Claude – barras verticais para variáveis qualitativas
            freq=filtered[chosen].astype(str).value_counts();top=freq.head(15).copy()
            if len(freq)>15:top.loc['Outras (agregado)']=freq.iloc[15:].sum()
            t=top.rename_axis('categoria').reset_index(name='internacoes')
            fig=px.bar(t,x='categoria',y='internacoes',title=f'Distribuição de {chosen}',labels={'internacoes':'Internações','categoria':'Categoria'},category_orders={'categoria':t.categoria.tolist()})
            fig.update_traces(name='Internações',showlegend=True);fig.update_xaxes(type='category');show_chart(fig,'dist_all','Contagem');show_note('A2')
        st.caption('Os gráficos categóricos agregam a cauda apenas para apresentação. O notebook e os CSVs preservam a distribuição completa de todas as categorias.')
        st.dataframe(filtered[NUMERIC].describe().T)
    with relations:
        # [IA] Claude – E4 com Pearson e Spearman para cada classe do desfecho
        cols=st.columns(2)
        for i,((m,k),corr) in enumerate(correlations_by_class(filtered).items()):
            corr=corr.rename(index=LABELS,columns=LABELS)
            with cols[i%2]:
                if corr.isna().all(axis=None):st.info(f'{m.title()} - {k}: registros insuficientes no recorte.');continue
                fig=px.imshow(corr,text_auto='.2f',color_continuous_scale='RdBu_r',zmin=-1,zmax=1,aspect='auto',title=f'E4 · {m.title()} - {k}',labels={'x':'Variável','y':'Variável','color':m.title()})
                fig.update_layout(height=560);show_chart(fig,f'E4_{i}')
        show_note('E4')
        a,b=st.columns(2)
        with a:heatmap('age','grupo_internacoes','M1')
        with b:heatmap('grupo_internacoes','grupo_emergencias','M2')
        st.caption('As matrizes são estratificações descritivas, sem ajuste causal. Grupos pequenos e pacientes repetidos limitam inferências.')
        x=st.selectbox('Eixo X',NUMERIC,index=0,format_func=lambda v:LABELS[v]);y=st.selectbox('Eixo Y',NUMERIC,index=3,format_func=lambda v:LABELS[v])
        sample=filtered.sample(min(len(filtered),4000),random_state=42)
        fig=px.scatter(sample,x=x,y=y,color='desfecho',opacity=.35,title=f'{LABELS[y]} × {LABELS[x]}',labels={**LABELS,'desfecho':'Reinternação'},color_discrete_map=COLORS)
        show_chart(fig,'I1');show_note('I1');st.caption(f'Amostra visual: {len(sample):,} linhas, semente 42. Demais estatísticas usam todo o recorte.')
        with st.expander('Relações de todos os atributos com o desfecho - base integral'):
            st.dataframe(tables['relacoes_com_alvo'],hide_index=True)

with story:
    st.subheader('Do histórico de atendimento à comunicação dos resultados')
    # [IA] Claude – narrativa a partir da estrutura de story_text
    narrativa=story_text(filtered)
    st.markdown('**Pergunta de pesquisa:** '+narrativa['pergunta'])
    rates=[rate_by(filtered,v) for v in ['number_inpatient','number_emergency']]
    ymax=min(100,max(t.percentual.max() for t in rates)*1.3+1)
    a,b=st.columns(2)
    for col,key,var,t in zip([a,b],['X1','X2'],['number_inpatient','number_emergency'],rates):
        with col:
            title=f'{key} · {t.percentual.iloc[0]:.1f}% a {t.percentual.iloc[-1]:.1f}% por histórico' if len(t)>1 else f'{key} · Apenas um grupo no recorte'
            fig=px.bar(t,x='grupo',y='percentual',text='percentual',custom_data=['n','casos'],title=title,labels={'grupo':LABELS[var]+' (ano anterior)','percentual':'Reinternações <30 dias (%)'})
            fig.update_traces(marker_color=['#cf593d' if g=='3 ou mais' else '#93a5b9' for g in t.grupo],texttemplate='%{text:.1f}%',name='Reinternação <30 dias',showlegend=True,hovertemplate='Grupo %{x}<br>%{y:.2f}%<br>Internações: %{customdata[0]}<br>Casos: %{customdata[1]}<extra></extra>')
            fig.update_yaxes(range=[0,ymax]);show_chart(fig,key);show_note(key);st.dataframe(t[['grupo','n','casos','percentual']],hide_index=True)
    # [IA] Claude – títulos do storytelling para o grupo preencher
    for titulo,campo in STORY_TITULOS:
        st.markdown(f'**{titulo}**\n\n{narrativa[campo]}')
    st.subheader('Sensibilidade à definição da coorte - base integral')
    st.dataframe(tables['sensibilidade_coortes'],hide_index=True)
    st.caption('A seleção de menor encounter_id é uma sensibilidade de representação por paciente, sem afirmar ordem temporal comprovada. A base não captura necessariamente atendimentos fora da rede de origem.')

with quality:
    st.subheader('Qualidade da base integral e decisões de tratamento')
    # [IA] Claude – auditoria filtrada, faltantes, duplicatas e Q1 em contagem
    st.dataframe(audit_positive(tables['auditoria_inconsistencias']),hide_index=True)
    st.markdown(TG.QUALIDADE)
    isna=raw.isna().sum().loc[lambda v:v>0].rename_axis('atributo').reset_index(name='isna_sum')
    st.dataframe(isna,hide_index=True);st.metric('Linhas duplicadas',int(raw.duplicated().sum()))
    st.subheader('Ausências')
    miss=tables['mecanismos_ausencia'].sort_values('n',ascending=False)
    st.dataframe(format_pct(miss.drop(columns='marcador')),hide_index=True)
    st.markdown(TG.ausencia_markdown())
    fig=px.bar(miss,x='n',y='atributo',color='tipo',orientation='h',text='n',title='Q1 · Registros faltantes por atributo',color_discrete_map=TIPOS_FALTANTE,labels={'n':'Contagem de registros','atributo':'Atributo','tipo':'Tipo de faltante'})
    fig.update_yaxes(categoryorder='array',categoryarray=miss.atributo.tolist()[::-1]);fig.update_layout(height=520);show_chart(fig,'Q1','Tipo de faltante');show_note('Q1')
    # [IA] Claude – heatmaps de ausência conjunta
    cols=st.columns(2)
    for i,(a,b) in enumerate(PARES_AUSENCIA):
        fig=px.imshow(missing_crosstab(raw,a,b),text_auto='d',color_continuous_scale='Magma',title=f'As ausências ocorrem juntas? {a} × {b}',labels={'x':f'{b} ausente','y':f'{a} ausente','color':'Internações'})
        with cols[i%2]:show_chart(fig,f'aus_{i}')
    with st.expander('Padrões de ausência por idade e desfecho'):
        st.dataframe(format_pct(tables['padroes_ausencia']),hide_index=True)
    st.subheader('Outliers: identificação, avaliação e preservação')
    st.dataframe(tables['outliers_iqr'].drop(columns='decisao',errors='ignore'),hide_index=True)  # [IA] Claude – sem a coluna decisao
    # [IA] Claude – marcador no lugar do texto e sem a tabela sensibilidade_log1p
    st.markdown(TG.OUTLIERS)
    st.image(str(ROOT/'out/parte_especifica/figuras/Q2.png'),caption='Q2 · Base integral: boxplots para triagem de extremos.');show_note('Q2')

with notebook_docs:
    st.subheader('Notas analíticas do recorte')
    st.caption('Os textos abaixo são as notas incorporadas ao projeto. Edições feitas nesta sessão podem ser exportadas. Se mudar os filtros, será aberto um conjunto de notas correspondente ao novo recorte.')
    exported={}
    for key,n in notes.items():
        text=f'O que mostra: {n["o_que_mostra"]}\n\nInterpretação: {n["interpretacao"]}\n\nEscolha visual: {n["escolha_visual"]}'
        with st.expander(f'{key} · {n["titulo"]}'):
            edited=st.text_area('Texto da nota',value=text,key=f'texto_{key}_{signature}',height=180)
        exported[key]={**n,'texto_da_sessao':edited}
    st.download_button('Baixar notas e filtros',json.dumps({'filtros':filter_description,'notas':exported},ensure_ascii=False,indent=2),'notas_analiticas.json','application/json')
    st.download_button('Baixar recorte CSV',filtered.to_csv(index=False).encode('utf-8-sig'),'diabetes_recorte.csv','text/csv')
    for name,title in [('relatorio.md','Relatório analítico'),('explicacao.md','Explicações e catálogo de requisitos')]:
        with st.expander(title):st.markdown((ROOT/name).read_text(encoding='utf-8'))
    # [IA] Claude – usa o PDF da Parte Específica gerado por documentos.py; o relatorio.pdf da raiz é o fallback
    pdf=next((p for p in [ROOT/'out'/'parte_especifica'/'relatorio_parte_especifica.pdf',ROOT/'relatorio.pdf'] if p.exists()),ROOT/'relatorio.pdf')
    if pdf.exists():st.download_button('Baixar relatório PDF',pdf.read_bytes(),'Relatorio_Parte_Especifica_Diabetes.pdf','application/pdf')
    st.caption('O relatório PDF usa a base integral. As notas e os gráficos ao vivo acompanham os filtros.')
with model:
    st.subheader("Classificação de reinternação em menos de 30 dias")
    st.write("Modelo de referência com regressão logística. O treino e o teste separam pacientes, para que internações da mesma pessoa não apareçam nos dois conjuntos.")
    st.caption("Este exemplo usa a base completa, independentemente dos filtros de exploração. Execute pelo botão para calcular as métricas.")
    if st.button("Treinar e avaliar modelo", type="primary"):
        from sklearn.compose import ColumnTransformer
        from sklearn.impute import SimpleImputer
        from sklearn.linear_model import LogisticRegression
        from sklearn.metrics import accuracy_score, precision_score, recall_score, roc_auc_score, confusion_matrix
        from sklearn.model_selection import GroupShuffleSplit
        from sklearn.pipeline import Pipeline
        from sklearn.preprocessing import OneHotEncoder, StandardScaler

        cat = ["age", "gender", "race", "insulin", "diabetesMed", "change"]
        X = raw[NUMERIC + cat]
        target = raw["readmitted"].eq("<30").astype(int)
        train, test = next(GroupShuffleSplit(n_splits=1, test_size=0.2, random_state=42).split(X, target, groups=raw["patient_nbr"]))
        numeric_pipe = Pipeline([("impute", SimpleImputer(strategy="median")), ("scale", StandardScaler())])
        categorical_pipe = Pipeline([("impute", SimpleImputer(strategy="constant", fill_value="Não informado")), ("encode", OneHotEncoder(handle_unknown="ignore"))])
        preprocess = ColumnTransformer([("num", numeric_pipe, NUMERIC), ("cat", categorical_pipe, cat)])
        classifier = Pipeline([("preprocess", preprocess), ("model", LogisticRegression(max_iter=1000, class_weight="balanced", random_state=42))])
        with st.spinner("Treinando e avaliando em pacientes separados..."):
            classifier.fit(X.iloc[train], target.iloc[train])
            prediction = classifier.predict(X.iloc[test])
            score = classifier.predict_proba(X.iloc[test])[:, 1]
        assert set(raw.iloc[train]["patient_nbr"]).isdisjoint(set(raw.iloc[test]["patient_nbr"]))
        values = {"Acurácia": accuracy_score(target.iloc[test], prediction),
                  "Precisão <30 dias": precision_score(target.iloc[test], prediction, zero_division=0),
                  "Recall <30 dias": recall_score(target.iloc[test], prediction, zero_division=0),
                  "ROC AUC": roc_auc_score(target.iloc[test], score)}
        for column, (label, value) in zip(st.columns(4), values.items()):
            column.metric(label, f"{value:.3f}")
        matrix = confusion_matrix(target.iloc[test], prediction, labels=[0, 1])
        fig = px.imshow(matrix, text_auto=True, color_continuous_scale="Blues", x=["Não <30", "<30"], y=["Não <30", "<30"],
                        title="Matriz de confusão — pacientes de teste", labels={"x": "Classe prevista", "y": "Classe observada", "color": "Internações"})
        show_chart(fig, "confusion")
        st.write(f"Treino: {len(train):,} internações. Teste: {len(test):,}. Interseção de pacientes: 0. Limiar de classificação: 0,5.")

st.divider()
st.caption('Fonte: Diabetes 130-US Hospitals for Years 1999-2008 · UCI. Associação descritiva em base histórica; a unidade de análise é a internação.')
