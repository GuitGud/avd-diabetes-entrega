"""EDA reproduzível, catálogo de visualizações e rastreabilidade da Parte Específica."""
from pathlib import Path
import csv
import json
import re
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
AGE_ORDER = [f'[{i}-{i+10})' for i in range(0, 100, 10)]
NUMERIC = ['time_in_hospital','num_lab_procedures','num_procedures','num_medications','number_outpatient','number_emergency','number_inpatient','number_diagnoses']
IDS = ['encounter_id','patient_nbr']
CODES = ['admission_type_id','discharge_disposition_id','admission_source_id']
OUTCOMES = {'NO':'Sem reinternação registrada','>30':'Após 30 dias','<30':'Em menos de 30 dias'}
ORDER = list(OUTCOMES.values())
COLORS = dict(zip(ORDER, ['#93a5b9','#27859b','#cf593d']))
LABELS = {'time_in_hospital':'Permanência (dias)','num_lab_procedures':'Exames laboratoriais','num_procedures':'Procedimentos','num_medications':'Medicamentos','number_outpatient':'Consultas ambulatoriais prévias','number_emergency':'Emergências prévias','number_inpatient':'Internações prévias','number_diagnoses':'Diagnósticos'}
BASE_DESCRIPTIONS = {'encounter_id':'Identificador da internação; não é medida quantitativa.','patient_nbr':'Identificador do paciente; permite reconhecer registros repetidos.','race':'Categoria demográfica registrada na fonte.','gender':'Sexo registrado; Unknown/Invalid é categoria sem informação válida.','age':'Faixa etária ordinal de dez anos.','weight':'Faixa de peso em kg (limites convertidos de libras e arredondados); não é um peso pontual.','admission_type_id':'Código nominal do tipo de admissão.','discharge_disposition_id':'Código nominal do destino na alta.','admission_source_id':'Código nominal da origem da admissão.','payer_code':'Categoria de pagador registrada.','medical_specialty':'Especialidade médica registrada.','diag_1':'Código textual do diagnóstico principal (ICD-9-CM).','diag_2':'Código textual do diagnóstico secundário (ICD-9-CM).','diag_3':'Código textual do diagnóstico adicional (ICD-9-CM).','max_glu_serum':'Categoria do teste de glicose; None significa não medido.','A1Cresult':'Categoria de HbA1c; None significa não medido.','change':'Indicador de mudança da medicação de diabetes.','diabetesMed':'Indicador de medicação para diabetes.','readmitted':'Rótulo original: <30, >30 ou NO; NO significa ausência de registro de reinternação.'}
SOURCE_URL = 'https://archive.ics.uci.edu/dataset/296/diabetes-130-us-hospitals-for-years-1999-2008'
PAPER_URL = 'https://pmc.ncbi.nlm.nih.gov/articles/PMC3996476/'
GROUPS = ['0','1','2','3 ou mais']

# [IA] Claude – constantes usadas pelas novas tabelas e gráficos
TEXTO_GRUPO = '[TEXTO DO GRUPO]'
LB_KG = 0.45359237
CLASSE_30 = 'Em menos de 30 dias'
CLASSE_DEMAIS = 'Demais categorias'
CORES_BINARIAS = {CLASSE_DEMAIS:'#c3ccd5', CLASSE_30:'#cf593d'}
CODIGOS_SEM_INFO = {'admission_type_id':[5,6,8],'discharge_disposition_id':[18,21,25,26],'admission_source_id':[9,15,17,20,21]}
TIPOS_FALTANTE = {'Marcador ?':'#27859b','Unknown/Invalid':'#cf593d','Código sem informação':'#93a5b9','None (exame)':'#e0a93f'}
PARES_AUSENCIA = [('payer_code','medical_specialty'),('weight','payer_code'),('weight','medical_specialty'),('diag_2','diag_3')]


# [IA] Claude – converte uma faixa de peso em libras para kg, arredondando os limites
def weight_to_kg(value):
    if pd.isna(value): return value
    return re.sub(r'\d+', lambda m: str(round(int(m.group())*LB_KG)), str(value))


WEIGHT_KG_ORDER = [weight_to_kg(f'[{i}-{i+25})') for i in range(0,200,25)] + [weight_to_kg('>200')]


# [IA] Claude – opção do grupo para remover as linhas com readmitted == "NO" (None = escolha pendente)
def apply_no_option(raw, remover_no):
    if remover_no not in (None, True, False):
        raise ValueError('REMOVER_NO deve ser True, False ou None.')
    return raw.loc[raw.readmitted.ne('NO')].reset_index(drop=True) if remover_no is True else raw


# [IA] Claude – guarda a opção para que o dashboard use a mesma base do notebook
def option_path(root): return Path(root)/'out/parte_especifica/opcao_remover_no.json'


def read_option(root):
    path=option_path(root)
    return json.loads(path.read_text(encoding='utf-8')) if path.exists() else None


def read_data(root=ROOT):
    raw = pd.read_csv(Path(root)/'data/parte_especifica/diabetic_data.csv', keep_default_na=False, na_values=['?'], low_memory=False,
                       dtype={k:'object' for k in ['diag_1','diag_2','diag_3','payer_code']})
    # [IA] Claude – troca "?" por np.nan antes de qualquer isna() e converte weight para kg
    texto = raw.select_dtypes(include='object').columns
    raw[texto] = raw[texto].mask(raw[texto].eq('?'), np.nan)
    raw['weight'] = raw['weight'].map(weight_to_kg)
    return raw


def code_mappings(root=ROOT):
    maps, current = {}, None
    with (Path(root)/'data/parte_especifica/IDS_mapping.csv').open(newline='') as f:
        for row in csv.reader(f):
            if not row or not row[0].strip():
                continue
            if row[0] in CODES:
                current=row[0]; maps[current]={}
            elif current:
                maps[current][int(row[0])]=row[1].strip()
    return maps


def semantic_type(c):
    if c in IDS: return 'Identificador'
    if c in NUMERIC: return 'Quantitativa discreta'
    if c in ['age','weight']: return 'Categórica ordinal em intervalos'
    if c == 'readmitted': return 'Categórica nominal - alvo'
    return 'Categórica nominal'


def schema_table(raw):
    records=[]
    for c in raw:
        description=BASE_DESCRIPTIONS.get(c, LABELS.get(c, f'Situação de uso e alteração de dose de {c}.'))
        records.append({'atributo':c,'dtype_python':str(raw[c].dtype),'tipo_semantico':semantic_type(c),'papel':'ID' if c in IDS else ('Alvo' if c=='readmitted' else 'Atributo'),
                        'descricao':description,'valores_distintos':int(raw[c].nunique(dropna=True)),'ausentes_interrogacao':int(raw[c].isna().sum()),'ausentes_pct':round(raw[c].isna().mean()*100,4),
                        'exemplos':' | '.join(map(str,raw[c].dropna().unique()[:4]))})
    return pd.DataFrame(records)


def prepare(raw):
    df=raw.copy()
    for c in df.select_dtypes(include='object'):
        df[c]=df[c].fillna('Não informado')
    df['desfecho']=df.readmitted.map(OUTCOMES)
    df['reinternacao_30']=df.readmitted.eq('<30').astype(int)
    df['sexo']=df.gender.map({'Male':'Masculino','Female':'Feminino','Unknown/Invalid':'Não informado'})
    df['grupo_internacoes']=history_group(df.number_inpatient)
    df['grupo_emergencias']=history_group(df.number_emergency)
    return df


def history_group(s):
    return pd.Categorical(s.clip(upper=3).map({0:'0',1:'1',2:'2',3:'3 ou mais'}),categories=GROUPS,ordered=True)


def rate_by(df, variable):
    tmp=df.assign(grupo=history_group(df[variable]))
    tab=tmp.groupby('grupo',observed=True)['reinternacao_30'].agg(n='size',casos='sum',taxa='mean').reset_index()
    tab['grupo']=tab.grupo.astype(str)
    tab['percentual']=tab.taxa*100
    return tab


def strata_table(df, a='age', b='grupo_internacoes'):
    tab=df.groupby([a,b],observed=True)['reinternacao_30'].agg(n='size',casos='sum',taxa='mean').reset_index()
    tab['percentual']=tab.taxa*100
    return tab


# [IA] Claude – tabela de faltantes sem as colunas de hipótese e tratamento
def missing_mechanisms(raw, root=ROOT):
    records=[]
    def add(c,tipo,marcador,n):
        if n: records.append({'atributo':c,'tipo':tipo,'marcador':marcador,'n':int(n),'percentual':n/len(raw)*100})
    for c in raw: add(c,'Marcador ?','?',raw[c].isna().sum())
    add('gender','Unknown/Invalid','Unknown/Invalid',raw.gender.eq('Unknown/Invalid').sum())
    for c, codes in CODIGOS_SEM_INFO.items(): add(c,'Código sem informação',','.join(map(str,codes)),raw[c].isin(codes).sum())
    for c in ['A1Cresult','max_glu_serum']: add(c,'None (exame)','None',raw[c].eq('None').sum())
    return pd.DataFrame(records)


# [IA] Claude – formata percentuais com 2 casas decimais e símbolo %
def format_pct(table, columns=('percentual',)):
    out=table.copy()
    for c in columns: out[c]=out[c].map(lambda v:f'{v:.2f}%')
    return out


# [IA] Claude – separa a estrutura em atributos qualitativos e quantitativos
# [IA] Claude – identificadores (encounter_id, patient_nbr) ficam fora das tabelas de qualitativos e quantitativos
def split_schema(schema):
    quant=schema.atributo.isin(NUMERIC);ids=schema.atributo.isin(IDS)
    return schema.loc[~quant&~ids].reset_index(drop=True), schema.loc[quant].reset_index(drop=True), schema.loc[ids].reset_index(drop=True)


# [IA] Claude – estatísticas das variáveis numéricas (kurtosis = excesso de curtose, padrão do pandas)
def numeric_stats(raw):
    t=raw[NUMERIC].agg(['mean','median','std','min','max','skew','kurt']).T
    return t.rename(columns={'skew':'skewness','kurt':'kurtosis'}).reset_index(names='atributo')


# [IA] Claude – verificações da auditoria com ocorrências maiores que zero
def audit_positive(audit):
    # [IA] Claude – sem as colunas marcador e decisao (texto automático antigo)
    return audit.loc[audit.ocorrencias.gt(0)].drop(columns=['marcador','decisao'],errors='ignore').reset_index(drop=True)


# [IA] Claude – tabela de contingência das ausências de dois atributos
def missing_crosstab(raw, a, b):
    d=raw[[a,b]].replace('?',np.nan).isna()
    t=pd.crosstab(d[a],d[b],rownames=[f'{a} ausente'],colnames=[f'{b} ausente'])
    t=t.reindex(index=[False,True],columns=[False,True],fill_value=0)
    nomes={False:'Não',True:'Sim'}
    return t.rename(index=nomes,columns=nomes)


# [IA] Claude – classe binária do desfecho para gráficos de duas cores e correlações
def binary_class(df):
    return pd.Series(np.where(df.reinternacao_30.eq(1),CLASSE_30,CLASSE_DEMAIS),index=df.index)


# [IA] Claude – matrizes de Pearson e Spearman para as duas classes do desfecho
def correlations_by_class(df):
    classe=binary_class(df)
    return {(m,k):df.loc[classe.eq(k),NUMERIC].corr(method=m) for m in ['pearson','spearman'] for k in [CLASSE_30,CLASSE_DEMAIS]}


# [IA] Claude – curva KDE gaussiana (regra de Scott) em escala de contagem por unidade
def kde_counts(values, points=300):
    s=pd.Series(values).dropna()
    if len(s)<2 or s.std()==0: return None
    f=s.value_counts(); h=s.std()*len(s)**(-1/5)
    x=np.linspace(s.min()-.5,s.max()+.5,points)
    z=(x[:,None]-f.index.to_numpy(dtype=float)[None,:])/h
    return x,(np.exp(-.5*z**2)*f.to_numpy()).sum(axis=1)/(h*np.sqrt(2*np.pi))


# [IA] Claude – distribuição acumulada empírica (ECDF)
def ecdf_table(values):
    f=pd.Series(values).dropna().value_counts().sort_index()
    return pd.DataFrame({'valor':f.index,'acumulada':f.cumsum().to_numpy()/f.sum()})


def missing_patterns(raw):
    rows=[]
    for c in raw.columns[raw.isna().any()]:
        for strat in ['age','readmitted']:
            t=raw.assign(ausente=raw[c].isna()).groupby(strat,dropna=False).ausente.agg(n='size',faltantes='sum',taxa='mean').reset_index()
            for r in t.to_dict('records'):
                rows.append({'atributo':c,'estratificador':strat,'grupo':r[strat],'n':r['n'],'faltantes':r['faltantes'],'percentual':r['taxa']*100})
    return pd.DataFrame(rows)


def consistency_checks(raw, root=ROOT):
    rows=[]
    def add(name,n,action,kind='Verificação'):
        rows.append({'verificacao':name,'ocorrencias':int(n),'tipo':kind,'decisao':action})
    add('Linhas inteiramente duplicadas',raw.duplicated().sum(),'Não excluir automaticamente; somente duplicatas efetivamente confirmadas seriam removidas.')
    add('encounter_id duplicado',raw.encounter_id.duplicated().sum(),'ID de internação deve ser único; duplicatas exigiriam reconciliação antes de análise.')
    add('Registros adicionais de pacientes já presentes',raw.patient_nbr.duplicated().sum(),'Não são erros: manter na coorte principal; comparar seleção de menor encounter_id por paciente.','Estrutura')
    for c in IDS+NUMERIC:
        s=pd.to_numeric(raw[c],errors='coerce')
        invalid=s.isna() | s.mod(1).ne(0) | s.lt(0)
        if c in IDS: invalid|=s.eq(0)
        if c=='time_in_hospital': invalid|=~s.between(1,14)
        add(f'Tipo/domínio numérico: {c}',invalid.sum(),'Não arredondar ou substituir valores inválidos silenciosamente; sinalizar para revisão.')
    domains={'age':AGE_ORDER,'weight':WEIGHT_KG_ORDER,'race':['Caucasian','AfricanAmerican','Asian','Hispanic','Other'],
             'gender':['Female','Male','Unknown/Invalid'],'readmitted':['NO','>30','<30'],'A1Cresult':['None','Norm','>7','>8'],'max_glu_serum':['None','Norm','>200','>300'],
             'change':['No','Ch'],'diabetesMed':['Yes','No']}
    medications=[c for c in raw if c not in set(BASE_DESCRIPTIONS)|set(NUMERIC)]
    domains.update({c:['No','Steady','Up','Down'] for c in medications})
    for c, allowed in domains.items():
        add(f'Categorias fora do domínio: {c}',(raw[c].notna() & ~raw[c].isin(allowed)).sum(),'Preservar fonte; sinalizar categorias não previstas em vez de convertê-las automaticamente.')
    for c, mapping in code_mappings(root).items():
        add(f'Código não presente em IDS_mapping: {c}',(~raw[c].isin(mapping)).sum(),'Manter e sinalizar código sem mapeamento; não confundir com código mapeado para NULL.')
    for c in ['diag_1','diag_2','diag_3']:
        ok=raw[c].astype('string').str.fullmatch(r'(?:\d{3}(?:\.\d{1,2})?|[EV]\d{2,3}(?:\.\d{1,2})?)',na=True)
        add(f'Formato ICD-9 não usual: {c}',(~ok).sum(),'Apenas triagem sintática; formato não valida o diagnóstico. Preservar original e consultar dicionário se houver ocorrência.')
    add('Sexo Unknown/Invalid',raw.gender.eq('Unknown/Invalid').sum(),'Exibir Não informado e manter registro.','Categoria sem informação')
    for c in ['num_lab_procedures','num_medications']:
        add(f'{c} igual a zero',raw[c].eq(0).sum(),'Preservar e destacar divergência entre valor registrado e critério geral de inclusão descrito na fonte. Não inventar valor positivo.','Alerta de metadados')
    return pd.DataFrame(rows)


def outlier_table(raw):
    rows=[]
    for c in NUMERIC:
        s=raw[c].dropna(); q1,q3=s.quantile([.25,.75]); iqr=q3-q1; lo=q1-1.5*iqr; hi=q3+1.5*iqr
        flag=(s<lo)|(s>hi)
        rows.append({'atributo':c,'min':float(s.min()),'q1':float(q1),'mediana':float(s.median()),'q3':float(q3),'max':float(s.max()),'iqr':float(iqr),'limite_inferior':float(lo),'limite_superior':float(hi),'sinalizados_iqr':int(flag.sum()),'sinalizados_pct':float(flag.mean()*100),'p99':float(s.quantile(.99)),'acima_p99':int(s.gt(s.quantile(.99)).sum()),
                     'decisao':'Manter: IQR zero em contagem com muitos zeros não torna todo valor positivo um erro. Aplicar log1p apenas em análise de sensibilidade.' if iqr==0 else 'Manter: valor estatisticamente extremo não comprova erro. Conservar contagens e comparar transformação log1p; não remover casos potencialmente relevantes ao alvo.'})
    return pd.DataFrame(rows)


def categorical_frequencies(raw):
    rows=[]
    for c in raw:
        if c in IDS+NUMERIC: continue
        for value,n in raw[c].fillna('Não informado').value_counts(dropna=False).items():
            rows.append({'atributo':c,'valor':str(value),'n':int(n),'percentual':n/len(raw)*100})
    return pd.DataFrame(rows)


def target_relations(df):
    rows=[]
    for c in [x for x in df.columns if x not in IDS+['readmitted','desfecho','reinternacao_30','sexo','grupo_internacoes','grupo_emergencias']]:
        if c in NUMERIC:
            for outcome,g in df.groupby('desfecho',observed=True):
                rows.append({'atributo':c,'tipo':'numérica','grupo':outcome,'n':len(g),'media':float(g[c].mean()),'mediana':float(g[c].median()),'casos_30':int(g.reinternacao_30.sum()),'taxa_30_pct':float(g.reinternacao_30.mean()*100)})
        else:
            t=df.groupby(c,observed=True)['reinternacao_30'].agg(n='size',casos_30='sum',taxa='mean').reset_index()
            for r in t.to_dict('records'):
                rows.append({'atributo':c,'tipo':'categórica','grupo':str(r[c]),'n':r['n'],'media':np.nan,'mediana':np.nan,'casos_30':r['casos_30'],'taxa_30_pct':r['taxa']*100})
    return pd.DataFrame(rows)


def sensitivity_table(df):
    living=df.loc[~df.discharge_disposition_id.isin([11,13,14,19,20,21])]
    unique=df.sort_values('encounter_id').drop_duplicates('patient_nbr')
    cohorts={'Todas as internações':df,'Menor encounter_id por paciente':unique,'Sem alta por óbito/hospice':living,'Menor ID por paciente, sem óbito/hospice':unique.loc[~unique.discharge_disposition_id.isin([11,13,14,19,20,21])]}
    rows=[]
    for cohort,g in cohorts.items():
        for var in ['number_inpatient','number_emergency']:
            for r in rate_by(g,var).to_dict('records'):
                rows.append({'coorte':cohort,'variavel':var,**r})
    return pd.DataFrame(rows)


# [IA] Claude – notas sem interpretação; campos de gráficos refeitos também ficam para o grupo
def chart_notes(df):
    g=TEXTO_GRUPO
    templates={
      'E1':('Distribuição etária',g,g),
      'E2':('Permanência por desfecho','Boxplots da permanência hospitalar nos três desfechos.','Boxplot resume mediana e dispersão. A tabela de outliers complementa os pontos omitidos da figura.'),
      'E3':('Medicamentos por internação',g,g),
      'E4':('Correlações por classe do desfecho',g,g),
      'M1':('Idade, histórico e desfecho','Mapa de calor da proporção <30 dias por idade e grupo de internações prévias.','A matriz combina duas variáveis explicativas e o desfecho; escala percentual fixa de 0 a 100 evita mudanças de escala entre recortes.'),
      'M2':('Dois históricos simultâneos','Mapa de calor da proporção <30 dias por internações prévias e emergências prévias.','Cruzamento de duas contagens categorizadas permite explorar o desfecho simultaneamente, sem sugerir ajuste causal.'),
      'I1':('Exploração interativa','Dispersão de duas variáveis numéricas, com cor por desfecho.','Marcadores com transparência reduzem sobreposição; a escolha dos eixos permite formular e testar visualmente perguntas.'),
      'A1':('Distribuição acumulada (ECDF) das variáveis numéricas',g,g),
      'A2':('Distribuições categóricas completas',g,g),
      'H1':('Histogramas numéricos por desfecho - parte 1',g,g),
      'H2':('Histogramas numéricos por desfecho - parte 2',g,g),
      'Q1':('Registros faltantes por atributo',g,g),
      'Q2':('Valores extremos','Boxplots das medidas numéricas e tabela de sinalização pelo IQR.','Boxplots e limites explícitos tornam a triagem reproduzível; nenhuma internação é excluída só por ser extrema.')}
    for key,var in [('X1','number_inpatient'),('X2','number_emergency')]:
        templates[key]=(f'Reinternação e {LABELS[var].lower()}','Proporção de readmitted=<30 para cada grupo de histórico.','Barras com eixo zero, porcentagens e contagens explicitadas comunicam a associação. Laranja destaca 3 ou mais; as duas figuras usam a mesma escala vertical no recorte.')
    for page in range(1,6): templates[f'A2_{page}']=(f'Distribuições categóricas - página {page}',g,g)
    # Textos do grupo (textos_grupo.py); None mantém o texto já existente
    from textos_grupo import NOTAS
    notas={}
    for k,v in templates.items():
        mostra,interp,visual=NOTAS.get(k,(None,None,None))
        notas[k]={'id':k,'titulo':v[0],'o_que_mostra':mostra or v[1],'interpretacao':interp or g,'escolha_visual':visual or v[2],'versao':'Notas do grupo'}
    return notas


# [IA] Claude – aceita a opção de remover "NO" e gera as novas tabelas
def run_analysis(root=ROOT, remover_no='salva'):
    root=Path(root); out=root/'out/parte_especifica';out.mkdir(parents=True,exist_ok=True)
    # [IA] Claude – sem argumento, reutiliza a opção salva pelo notebook
    if isinstance(remover_no,str) and remover_no=='salva': remover_no=read_option(root)
    raw=apply_no_option(read_data(root),remover_no);df=prepare(raw)
    option_path(root).write_text(json.dumps(remover_no),encoding='utf-8')
    tables={'estrutura_atributos':schema_table(raw),'auditoria_inconsistencias':consistency_checks(raw,root),'mecanismos_ausencia':missing_mechanisms(raw,root),
            'padroes_ausencia':missing_patterns(raw),'outliers_iqr':outlier_table(raw),'frequencias_categoricas':categorical_frequencies(raw),'relacoes_com_alvo':target_relations(df),
            'taxas_internacoes':rate_by(df,'number_inpatient'),'taxas_emergencias':rate_by(df,'number_emergency'),'multivariada_idade_historico':strata_table(df),
            'multivariada_dois_historicos':strata_table(df,'grupo_internacoes','grupo_emergencias'),'sensibilidade_coortes':sensitivity_table(df),
            'descritiva_numerica':raw[NUMERIC].describe(percentiles=[.01,.25,.5,.75,.95,.99]).T.reset_index(names='atributo'),
            'correlacao_pearson':raw[NUMERIC].corr().reset_index(names='atributo'),'correlacao_spearman':raw[NUMERIC].corr(method='spearman').reset_index(names='atributo')}
    # [IA] Claude – tabelas das seções 4 e 8
    tables['estrutura_qualitativos'],tables['estrutura_quantitativos'],tables['estrutura_identificadores']=split_schema(tables['estrutura_atributos'])
    tables['estatisticas_numericas']=numeric_stats(raw)
    for (m,k),t in correlations_by_class(df).items():
        tables[f"correlacao_{m}_{'menos30' if k==CLASSE_30 else 'demais'}"]=t.reset_index(names='atributo')
    for name,t in tables.items(): t.to_csv(out/f'{name}.csv',index=False,encoding='utf-8-sig')
    # Comparação de escala e extremos com transformação monotônica, sem apagar valores.
    tables['sensibilidade_log1p']=pd.DataFrame({'atributo':NUMERIC,'pearson_alvo':[df[c].corr(df.reinternacao_30) for c in NUMERIC],
                                               'pearson_log1p_alvo':[np.log1p(df[c]).corr(df.reinternacao_30) for c in NUMERIC]})
    tables['sensibilidade_log1p'].to_csv(out/'sensibilidade_log1p.csv',index=False,encoding='utf-8-sig')
    # [IA] Claude – registra a opção usada no resumo
    summary={'remover_no':remover_no,'n_internacoes':len(raw),'n_pacientes':int(raw.patient_nbr.nunique()),'n_atributos':len(raw.columns),'casos_30':int(df.reinternacao_30.sum()),'taxa_30_pct':float(df.reinternacao_30.mean()*100),
             'duplicatas_completas':int(raw.duplicated().sum()),'duplicatas_encounter_id':int(raw.encounter_id.duplicated().sum()),'ocorrencias_extremas_por_atributo':int(tables['outliers_iqr'].sinalizados_iqr.sum()),
             'n_verificacoes':len(tables['auditoria_inconsistencias']),'source_sha256':__import__('hashlib').sha256((root/'data/parte_especifica/diabetic_data.csv').read_bytes()).hexdigest()}
    (out/'resumo.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf-8')
    (out/'notas_analiticas.json').write_text(json.dumps(chart_notes(df),ensure_ascii=False,indent=2),encoding='utf-8')
    return raw,df,tables,summary


if __name__=='__main__':
    _,_,_,summary=run_analysis()
    print(json.dumps(summary,ensure_ascii=False,indent=2))
