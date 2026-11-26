"""Gera relatório PDF, relatório Markdown e catálogo explicativo a partir da EDA."""
from pathlib import Path
import json
from xml.sax.saxutils import escape
import pandas as pd
from analise import ROOT, NUMERIC, LABELS, chart_notes, SOURCE_URL, PAPER_URL
# [IA] Claude – funções de formatação das novas tabelas
from analise import TEXTO_GRUPO, format_pct, audit_positive
import textos_grupo as TG


def mdtable(frame, limit=None):
    f=frame.head(limit) if limit else frame
    def cell(x):
        if pd.isna(x):return ''
        if isinstance(x,float):return f'{x:.3f}'
        return str(x).replace('|','/').replace('\n',' ')
    return '| '+' | '.join(map(str,f.columns))+' |\n| '+' | '.join(['---']*len(f.columns))+' |\n'+'\n'.join('| '+' | '.join(cell(x) for x in row)+' |' for row in f.itertuples(index=False,name=None))


def requirements_catalog():
    rows=[
      ('E01','Exploração - estrutura e tipos','estrutura_atributos.csv (50 atributos)','Notebook: Estrutura; painel: Exploração > Estrutura'),
      ('E02','Exploração - faltantes e cobertura','mecanismos_ausencia.csv; padroes_ausencia.csv','Notebook: Qualidade; painel: Qualidade'),
      ('E03','Exploração - inconsistências','auditoria_inconsistencias.csv (54 verificações)','Notebook: Qualidade; relatório: Qualidade'),
      ('E04','Exploração - outliers','outliers_iqr.csv; figura Q2; extremos simultâneos (medicamentos × internações prévias)','Notebook e painel: Qualidade; relatório: Extremos'),
      ('E05','Exploração - mecanismo de ausência','Hipóteses por atributo; limites de MCAR/MAR/MNAR','Relatório: Ausências; explicações: decisões D01-D04'),
      ('E06','Exploração - tratamento justificado','Preservação de linhas, categorias explícitas e sensibilidades','Relatório: Qualidade; explicações: registro de decisões'),
      ('E07','Exploração - distribuições completas','descritiva_numerica.csv; frequencias_categoricas.csv; A1 e A2.1-A2.5','Notebook: Distribuições; painel: seletor de atributos'),
      ('E08','Exploração - relações com o desfecho','relacoes_com_alvo.csv (47 atributos); Pearson e Spearman','Notebook: Relações; painel: Exploração > Relações'),
      ('E09','Exploração - relações multivariadas','M1: idade × histórico × alvo; M2: dois históricos × alvo','Notebook, painel e relatório: Relações multivariadas'),
      ('S01','Storytelling - pergunta e público','Gestores de qualidade e analistas; pergunta explícita','Notebook e painel: Pergunta e narrativa; relatório: Abertura'),
      ('S02','Storytelling - percurso e mensagem','Qualidade > distribuições > proporções > estratos > X1/X2','Relatório: Storytelling; explicações: etapas 3-7'),
      ('S03','Storytelling - resposta à pergunta','Proporções, diferença em pontos percentuais e limites','Painel: resposta do recorte; relatório: Resposta à pergunta'),
      ('V01','Visualizações - 4 exploratórias e 2 explanatórias','E1, E2, E3, E4; X1 e X2, com notas individuais','Notebook, relatório e painel'),
      ('V02','Visualizações - escolhas e atributos pré-atentivos','Justificativas por figura: posição, cor, escala, agregação','Notas analíticas; relatório: catálogo visual'),
      ('V03','Visualizações - títulos, eixos, legendas e escalas','Identificação explícita; eixos percentuais com zero; escalas compartilhadas','Figuras E1-E4 e X1-X2; testes de estrutura'),
      ('V04','Dashboard - organização e interação','Abas, filtros interligados, eixos configuráveis e exportação','src/parte_especifica/dashboard.py'),
      ('N01','Notas analíticas','O que mostra, interpretação e escolha visual por figura','notas_analiticas.json; relatório; painel: Notas e catálogo'),
      ('N02','Relatório analítico','Documento com método, evidências, gráficos e resposta à pergunta','relatorio.pdf e relatorio.md'),
      ('R01','Rastreabilidade e execução','Tabelas, SHA-256 da fonte, scripts, dependências e verificações','explicacao.md; resumo.json; validacao.json; README.md'),
    ]
    return pd.DataFrame([{'id':a,'criterio':b,'evidencia':c,'onde_encontrar':d,'situacao':'Implementado no material; avaliação acadêmica cabe à docente.'} for a,b,c,d in rows])


# [IA] Claude – estrutura do storytelling sem textos
STORY_TITULOS=[('Público-alvo','publico'),('Percurso','percurso'),('Resposta à pergunta','resposta'),('Mensagem central','mensagem'),('Justificativas visuais','visuais'),('Limitações','limites')]


def story_text(df):
    return {
      'pergunta':TG.PERGUNTA,
      **{campo:TG.STORY.get(campo,TEXTO_GRUPO) for _,campo in STORY_TITULOS}}


def create_documents(raw,df,tables,summary,figures,root=ROOT):
    root=Path(root);out=root/'out/parte_especifica';catalog=requirements_catalog();catalog.to_csv(out/'mapa_requisitos.csv',index=False,encoding='utf-8-sig')
    notes=chart_notes(df);story=story_text(df)
    (out/'notas_analiticas.json').write_text(json.dumps(notes,ensure_ascii=False,indent=2),encoding='utf-8')
    # Contagens de sinalização por atributo não representam pacientes ou linhas únicas.
    schema=tables['estrutura_atributos'];audit=tables['auditoria_inconsistencias'];miss=tables['mecanismos_ausencia'];ext=tables['outliers_iqr']
    med=tables['descritiva_numerica']
    cat=tables['frequencias_categoricas'].sort_values('n',ascending=False).drop_duplicates('atributo').sort_values('atributo')
    # [IA] Claude – marcador nos textos que repetiam conteúdo removido ou descreviam gráficos substituídos
    quality_text=TG.QUALIDADE;missing_text=TG.AUSENCIA_TEXTO;missing_decisions=TG.ausencia_texto_simples()
    outlier_text=TG.OUTLIERS+'\n\nExtremos simultâneos (medicamentos × internações prévias): '+TG.EXTREMOS_SIMULTANEOS['o_que_mostra']+' '+TG.EXTREMOS_SIMULTANEOS['interpretacao']
    distribution_text=TG.DISTRIBUICAO+'\n\n'+TG.assimetria_texto_simples()
    partes_text='\n'.join(f'{i}. {t} ({fig})' for i,(_,t,fig) in enumerate(TG.PERGUNTA_PARTES,1))
    c1_text=TG.C1_INTRO+'\n\n'+TG.C1_NOTA['interpretacao']
    relations_text='O catálogo de relações inclui os 47 atributos originais que não são IDs nem o próprio alvo. Para medidas numéricas, há médias e medianas por desfecho; para categorias, contagens e proporções <30 dias. Pearson e Spearman são calculados separadamente. M1 cruza idade, histórico de internações e desfecho; M2 cruza internações prévias, emergências prévias e desfecho. Cada célula tem denominador e numerador exportados. A apresentação é descritiva, sem equiparar correlação, estratificação ou associação a efeito causal.'
    sensitivity_text='A comparação inclui quatro coortes: todas as internações; uma linha por paciente pelo menor encounter_id; exclusão de altas por óbito/hospice (códigos 11, 13, 14, 19, 20 e 21); e a combinação das duas escolhas. A base integral é o ponto de partida, e os outros recortes mostram a dependência dos resultados das decisões de seleção. Não se afirma que a seleção pelo ID reconstrua a primeira internação em ordem temporal nem que reproduza exatamente a coorte do artigo.'
    sections=[
      '# Relatório da Parte Específica - Diabetes e reinternação hospitalar',
      '## 1. Pergunta, público e resposta','**Pergunta:** '+story['pergunta'],partes_text.replace('\n','\n\n'),'**Público-alvo:** '+story['publico'],story['resposta'],story['mensagem'],
      '## 2. Dados, unidade de análise e estrutura',f'Base: {summary["n_internacoes"]:,} internações; {summary["n_pacientes"]:,} pacientes; {summary["n_atributos"]} atributos originais. São {summary["casos_30"]:,} registros <30 dias'.replace(',','.').replace(';',',')+f' ({summary["taxa_30_pct"]:.2f}%)'.replace('.',',')+'. Cada linha é uma internação. A classe positiva é estritamente o rótulo <30; >30 e NO formam o complemento nas proporções binárias.',
      'A fonte é o conjunto UCI [1]. O CSV original permanece intacto, e o SHA-256 está em resumo.json. A tabela abaixo distingue tipo de armazenamento e tipo semântico.',mdtable(schema),
      '## 3. Qualidade e inconsistências',quality_text,mdtable(audit_positive(audit)),
      '## 4. Mecanismos de ausência e tratamento',missing_text,missing_decisions,mdtable(format_pct(miss.drop(columns='marcador'))),'![Q1 - Ausências](out/parte_especifica/figuras/Q1.png)',
      'Os padrões estratificados completos estão em out/parte_especifica/padroes_ausencia.csv.',
      '## 5. Outliers: identificação, avaliação e decisão',outlier_text,mdtable(ext.drop(columns='decisao',errors='ignore')),'![Q2 - Extremos](out/parte_especifica/figuras/Q2.png)',
      '## 6. Distribuições de todos os atributos',distribution_text,mdtable(med),mdtable(cat),
      '## 7. Relações multivariadas e sensibilidades',relations_text,notes['M1']['interpretacao'],notes['M2']['interpretacao'],'![M1 - Idade e histórico](out/parte_especifica/figuras/M1.png)','![M2 - Dois históricos](out/parte_especifica/figuras/M2.png)',sensitivity_text,mdtable(tables['sensibilidade_coortes']),
      '### Comparação das bases: com e sem as linhas NO (C1)',c1_text,'![C1 - Bases com e sem NO](out/parte_especifica/figuras/C1.png)',
      '## 8. Storytelling registrado',story['percurso'],story['mensagem'],story['visuais'],story['limites'],
      '## 9. Catálogo das seis visualizações principais e notas analíticas']
    for key in ['E1','E2','E3','E4','X1','X2']:
        n=notes[key];sections.extend([f'### {key}. {n["titulo"]}',f'![{key}](out/parte_especifica/figuras/{key}.png)','**O que mostra:** '+n['o_que_mostra'],'**Interpretação:** '+n['interpretacao'],'**Escolha visual:** '+n['escolha_visual']])
    sections.append('## 10. Notas das visualizações complementares')
    for key,n in notes.items():
        if key in ['E1','E2','E3','E4','X1','X2']:continue
        sections.extend([f'### {key}. {n["titulo"]}',n['o_que_mostra'],n['interpretacao'],n['escolha_visual']])
    sections.extend(['## 11. Catálogo de atendimento aos critérios',mdtable(catalog),'Os pesos da Parte Específica totalizam 6,0 pontos. O mapa registra evidências entregues, sem estimar nota ou certificar decisões acadêmicas da docente.',
                     '## 12. Limitações e referências',story['limites'],'## Declaração de uso de IA',TG.DECLARACAO_IA,
                     '[1] Clore, J.; Cios, K.; DeShazo, J.; Strack, B. (2014). Diabetes 130-US Hospitals for Years 1999-2008. UCI. DOI: 10.24432/C5230J. '+SOURCE_URL,
                     '[2] Strack, B. et al. (2014). Impact of HbA1c Measurement on Hospital Readmission Rates. DOI: 10.1155/2014/781670. '+PAPER_URL])
    (root/'relatorio.md').write_text('\n\n'.join(sections)+'\n',encoding='utf-8')
    decisions=pd.DataFrame([
      ('D01','Ausências literais ?','Preservar linhas e usar Não informado nas categorias.','Evita exclusão de coortes com cobertura desigual; fonte original preservada.'),
      ('D02','Peso em intervalos e muito ausente','Não imputar valor pontual; não incluir no modelo demonstrativo.','Os intervalos não são uma medida exata e a cobertura não sustenta preenchimento numérico simples.'),
      ('D03','None em A1Cresult/max_glu_serum','Manter como não realizado.','A categoria possui significado de processo descrito na fonte [2].'),
      ('D04','Códigos administrativos sem informação','Decodificar e separar das medidas numéricas.','Não há significado quantitativo para a média de códigos nominais.'),
      ('D05','Sexo Unknown/Invalid','Exibir Não informado; manter o registro.','Não inventa categoria e conserva rastreabilidade.'),
      ('D06','Repetição de paciente','Manter na base principal e comparar seleção de uma linha por paciente.','Várias internações do mesmo paciente não são duplicatas integrais.'),
      ('D07','Outliers por IQR','Preservar valores; documentar e comparar log1p.','Extremo não comprova erro e pode representar histórico relevante.'),
      ('D08','Categorias de alta cardinalidade','Agrupar Outras apenas no gráfico.','Melhora a leitura sem apagar categorias da tabela completa.'),
      ('D09','Grupos de histórico','0, 1, 2 e 3 ou mais, com n e casos.','Reduz fragmentação e mantém uma ordem de leitura para comparação.'),
      ('D10','Óbito/hospice e representação por paciente','Disponibilizar análise de sensibilidade explícita.','Mostra efeitos da composição do denominador; não altera silenciosamente a base.'),
      ('D11','Correlação e estratos','Apresentar Pearson, Spearman, M1 e M2 sem alegar causalidade.','Controles observacionais disponíveis são limitados e há repetição de pacientes.'),
      ('D12','Modelo demonstrativo','Dividir por paciente e ajustar pré-processamento apenas no treino.','Reduz vazamento entre conjuntos; variáveis do período de internação não configuram previsão no momento da admissão.')
    ],columns=['id','situacao','decisao','justificativa'])
    decisions.to_csv(out/'registro_decisoes.csv',index=False,encoding='utf-8-sig')
    explanation=[
      '# Explicações do projeto e catálogo de requisitos',
      '## 1. O que foi finalizado e onde localizar',
      'O notebook reúne EDA executável com tabelas e gráficos, documentação das decisões, notas analíticas, narrativa da pesquisa e inicialização do Streamlit. O relatório PDF e sua versão Markdown usam a base integral. O dashboard permite recalcular o recorte e exportar dados e notas. Este material cobre a Parte Específica; não inclui a Parte Comum de K-Means sobre Obesity ou Wine Quality.',
      mdtable(catalog),
      '## 2. Arquivos e responsabilidades',
      '- `src/parte_especifica/analise.py`: leitura, tipos semânticos, auditoria, faltantes, extremos, frequências, relações, estratos, sensibilidades e notas.\n- `src/parte_especifica/figuras.py`: figuras estáticas reproduzíveis para notebook e relatório.\n- `src/parte_especifica/documentos.py`: relatório PDF, relatório Markdown, README e esta explicação.\n- `src/parte_especifica/dashboard.py`: filtros, abas, gráficos ao vivo, notas e exportação.\n- `data/parte_especifica/`: CSVs originais.\n- `out/parte_especifica/`: evidências em CSV, JSON e PNG.\n- `relatorio.pdf` e `relatorio.md`: relatório analítico da base integral.\n- `requirements.txt`: versões de dependências.\n- `validacao.json`: resultado das verificações locais.\n- `DATA_SOURCE.md`: referência e licença dos dados.',
      '## 3. Ordem das etapas no Colab',
      '1. Instalar dependências em Python 3.11 ou superior.\n2. Restaurar o pacote incorporado e conferir seu SHA-256.\n3. Ler os dados sem converter automaticamente None em ausente; executar a EDA e regenerar tabelas, gráficos e documentos.\n4. Exibir estrutura e tipos.\n5. Inspecionar qualidade, hipóteses de ausência e decisões de tratamento.\n6. Analisar distribuições e valores extremos.\n7. Analisar relações com o alvo, cruzamentos multivariados e sensibilidades.\n8. Ler o storytelling e as seis visualizações principais, com suas notas.\n9. Consultar o catálogo de requisitos.\n10. Iniciar o Streamlit e exibir o painel dentro do notebook.',
      '## 4. Estrutura e tipos de atributos',
      f'A base possui {len(raw):,} linhas'.replace(',','.')+f' e {len(raw.columns)} colunas: 2 identificadores, 8 medidas numéricas, 39 atributos categóricos explicativos e 1 alvo categórico. O catálogo lista todos os 50 atributos, dtype, tipo semântico, papel, cardinalidade, faltantes e exemplos. Identificadores não entram na correlação. Códigos de admissão e alta são nominais. Idade e peso são intervalos ordenados; diagnósticos são códigos textuais.',
      '## 5. Qualidade, mecanismos e decisões justificadas',quality_text,missing_text,missing_decisions,mdtable(decisions),
      '## 6. Detecção e avaliação de outliers',outlier_text,mdtable(ext[['atributo','iqr','limite_inferior','limite_superior','sinalizados_iqr','sinalizados_pct']]),
      '## 7. Distribuições e relações multivariadas',distribution_text,relations_text,sensitivity_text,
      '## 8. Pergunta, público-alvo e storytelling',story['pergunta'],partes_text,c1_text,story['publico'],story['percurso'],story['resposta'],story['mensagem'],story['visuais'],
      '## 9. Notas analíticas catalogadas por visualização']
    for key,n in notes.items():
        explanation.extend([f'### {key} - {n["titulo"]}', '**O que mostra:** '+n['o_que_mostra'],'**Interpretação:** '+n['interpretacao'],'**Escolha visual:** '+n['escolha_visual']])
    explanation.extend([
      '## 10. Interface e comportamento dos filtros',
      'As abas separam Exploração, Pergunta e narrativa, Qualidade, Notas e catálogo e Classificação. Os filtros de idade, sexo, insulina e permanência afetam os seis gráficos principais e a narrativa. Há sensibilidades opcionais de uma linha por paciente e exclusão de altas por óbito/hospice. A auditoria de qualidade usa explicitamente a base integral, inclusive a figura Q2. O seletor de atributos cobre todas as variáveis analíticas. A dispersão usa até 4.000 pontos para manter resposta rápida; indicadores e seis gráficos principais usam o recorte inteiro. Filtros sem resultados mostram mensagem em vez de causar exceção.',
      '## 11. Modelo de classificação: papel e limites',
      'A regressão logística é opcional e usa a base completa, como indicado na interface. GroupShuffleSplit separa pacientes com semente 42 e fração de teste de 20%. A imputação e a padronização numéricas e a codificação categórica são ajustadas apenas no treino. IDs e rótulo não entram como preditores. Há acurácia, precisão, recall, ROC AUC e matriz de confusão. Pesos de classe balanceados e limiar 0,5 são explícitos. O modelo não substitui a EDA ou a Parte Comum e não representa validação clínica prospectiva.',
      '## 12. Execução no Colab e exportação',
      'Executar tudo instala dependências, restaura dados e código e apresenta a EDA. A última célula inicia o Streamlit como subprocesso, verifica /_stcore/health e usa google.colab.output.serve_kernel_port_as_iframe. O endereço localhost do computador pessoal não aponta para o servidor remoto. O iframe depende de sessão autenticada e runtime conectado. A célula pode ser reexecutada e encerra somente o processo anterior que ela mesma iniciou. CORS e proteção XSRF permanecem habilitados. O notebook contém os dados, sem exigir upload de CSV, montagem de Drive ou chave de túnel. O PDF já incluído pode ser baixado; o recorte CSV e as notas podem ser exportados pelo painel.',
      '## 13. Verificações e critérios de conclusão',
      'As verificações incluem integridade da base, catálogo de 50 atributos, cobertura de 47 relações com o alvo, consistência de numeradores e denominadores, tratamento do marcador None, casos com filtros vazios, construção dos gráficos, separação de pacientes no modelo e execução das células de EDA. O registro validacao.json contém os resultados efetivamente obtidos. A abertura e a execução dentro de uma conta Google dependem da autenticação no Colab e não são inferidas dos testes locais. Não se atribui pontuação automaticamente: o catálogo comprova material disponível para avaliação da docente.',
      '## 14. Limitações e referências',story['limites'],
      '[1] UCI, Diabetes 130-US Hospitals for Years 1999-2008. DOI 10.24432/C5230J. '+SOURCE_URL,
      '[2] Strack et al., 2014. DOI 10.1155/2014/781670. '+PAPER_URL,
      '[3] API do Colab: https://github.com/googlecolab/colabtools/blob/main/google/colab/output/_util.py',
      '[4] Streamlit: https://docs.streamlit.io/develop/api-reference/configuration/config.toml'
    ])
    (root/'explicacao.md').write_text('\n\n'.join(explanation)+'\n',encoding='utf-8')
    # README.md é mantido à mão na raiz (cobre as duas partes); não é mais sobrescrito aqui.
    create_pdf(root/'out'/'parte_especifica'/'relatorio_parte_especifica.pdf',raw,df,tables,summary,figures,notes,story,catalog,quality_text,missing_text,missing_decisions,outlier_text,distribution_text,relations_text,sensitivity_text,partes_text,c1_text)
    return catalog


def create_pdf(path,raw,df,tables,summary,figures,notes,story,catalog,*paragraphs):
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_LEFT
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from matplotlib import font_manager
    regular=font_manager.findfont('DejaVu Sans');bold=font_manager.findfont(font_manager.FontProperties(family='DejaVu Sans',weight='bold'))
    for name,file in [('AVD',regular),('AVD-Bold',bold)]:
        if name not in pdfmetrics.getRegisteredFontNames():pdfmetrics.registerFont(TTFont(name,file))
    pdfmetrics.registerFontFamily('AVD',normal='AVD',bold='AVD-Bold',italic='AVD',boldItalic='AVD-Bold')
    styles=getSampleStyleSheet()
    for name in ['Normal','BodyText','Title','Heading1','Heading2','Heading3']:
        styles[name].fontName='AVD-Bold' if name!='Normal' and name!='BodyText' else 'AVD'
        styles[name].textColor=colors.HexColor('#17354b')
    styles['BodyText'].fontSize=9;styles['BodyText'].leading=13;styles['BodyText'].spaceAfter=9
    styles['Title'].fontSize=25;styles['Title'].leading=31
    styles['Heading1'].fontSize=16;styles['Heading1'].leading=21;styles['Heading1'].spaceBefore=12
    styles['Heading2'].fontSize=12;styles['Heading2'].leading=16
    styles.add(ParagraphStyle('SmallAVD',fontName='AVD',fontSize=7,leading=9,textColor=colors.HexColor('#17354b')))
    styles.add(ParagraphStyle('TableAVD',fontName='AVD',fontSize=6.7,leading=9,textColor=colors.HexColor('#17354b')))
    story_flow=[];available=499
    def p(text,kind='BodyText'):story_flow.append(Paragraph(escape(str(text)).replace('\n','<br/>'),styles[kind]))
    def h(text):p(text,'Heading1')
    def table(frame,widths=None):
        data=[[Paragraph(escape(str(c)),styles['TableAVD']) for c in frame.columns]]
        for r in frame.itertuples(index=False,name=None):
            data.append([Paragraph(escape('' if pd.isna(v) else (f'{v:.2f}' if isinstance(v,float) else str(v))),styles['TableAVD']) for v in r])
        tab=Table(data,colWidths=widths or [available/len(frame.columns)]*len(frame.columns),repeatRows=1,hAlign='LEFT')
        tab.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#deebf1')),('VALIGN',(0,0),(-1,-1),'TOP'),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f4f7f9')]),('BOTTOMPADDING',(0,0),(-1,-1),5),('TOPPADDING',(0,0),(-1,-1),5),('LINEBELOW',(0,0),(-1,0),.5,colors.HexColor('#8198a8'))]));story_flow.append(tab);story_flow.append(Spacer(1,12))
    def image(key,max_h=300):
        from PIL import Image as PILImage
        pp=figures[key]
        with PILImage.open(pp) as im:w,hh=im.size
        scale=min(available/w,max_h/hh);story_flow.append(Image(str(pp),width=w*scale,height=hh*scale));story_flow.append(Spacer(1,8))
    def note(key):
        n=notes[key]
        for label,field in [('O que mostra','o_que_mostra'),('Interpretação','interpretacao'),('Escolha visual','escolha_visual')]:p(f'{label}: {n[field]}')
    p('PROJETO AVD / PARTE ESPECÍFICA','Heading2');p('Diabetes e reinternação hospitalar','Title');p('Relatório de exploração, comunicação e dashboard interativo','Heading2')
    # [IA] Claude – separador de milhar com ponto
    p(f'{summary["n_internacoes"]:,} internações | {summary["n_pacientes"]:,} pacientes | 50 atributos originais'.replace(',','.'))
    h('1. Pergunta, público e resposta');p(story['pergunta']);p(paragraphs[7]);p('Público-alvo: '+story['publico']);p(story['resposta']);p(story['mensagem']);p('Unidade de análise: internação. Dados históricos de 1999-2008. Fonte: UCI [1]. A classe positiva é o rótulo <30; o complemento reúne >30 e NO.');p(story['limites'])
    story_flow.append(PageBreak());h('2. Estrutura e tipos de atributos');p('A tabela abaixo lista as 50 colunas da base. Para cada uma, mostramos como o dado está gravado no arquivo (dtype_python) e o que ele significa na análise (tipo_semantico). As duas coisas nem sempre coincidem: admission_type_id, por exemplo, é gravado como número inteiro, mas é uma categoria (o código 1 não é "menor" que o código 3), e por isso não entra em médias nem em correlações. A coluna Distintos mostra quantos valores diferentes cada atributo tem, e a coluna ? (%) mostra a porcentagem marcada com "?". Exemplos e a descrição completa estão em estrutura_atributos.csv.')
    schema=tables['estrutura_atributos'][['atributo','dtype_python','tipo_semantico','valores_distintos','ausentes_pct']].rename(columns={'valores_distintos':'Distintos','ausentes_pct':'? (%)'})
    table(schema,[125,63,173,65,73])
    h('3. Qualidade e inconsistências');p(paragraphs[0]);aud=tables['auditoria_inconsistencias'];p(f'{len(aud)} verificações estão registradas. Ocorrências não nulas abaixo; verificações com zero também constam do CSV completo.')
    # [IA] Claude – tabela de qualidade sem a coluna decisao
    table(audit_positive(aud)[['verificacao','ocorrencias','tipo']],[300,90,109])
    h('4. Mecanismos de ausência e tratamento');p(paragraphs[1]);miss=tables['mecanismos_ausencia'];table(format_pct(miss[['atributo','tipo','n','percentual']]),[160,140,100,99]);image('Q1',240);note('Q1')
    p('Hipóteses de ausência e tratamento','Heading2');p(paragraphs[2])
    h('5. Outliers e decisão de preservação');p(paragraphs[3]);ext=tables['outliers_iqr'];table(ext[['atributo','iqr','limite_inferior','limite_superior','sinalizados_iqr','sinalizados_pct']],[120,45,75,75,98,86]);image('Q2',260);note('Q2')
    h('6. Distribuições completas');p(paragraphs[4]);table(tables['descritiva_numerica'][['atributo','mean','50%','min','max']],[190,80,80,74,75]);image('A1',270);note('A1')
    # [IA] Claude – histogramas por desfecho no PDF
    for key in ['H1','H2']:image(key,600);note(key)
    p('Categoria mais frequente de cada atributo categórico. O CSV inclui a distribuição integral, não só o modo.');cat=tables['frequencias_categoricas'].sort_values('n',ascending=False).drop_duplicates('atributo').sort_values('atributo');table(cat,[145,180,80,94])
    h('7. Relações multivariadas');p(paragraphs[5]);image('M1',300);note('M1');image('M2',260);note('M2')
    h('8. Sensibilidade de coortes');p(paragraphs[6]);sens=tables['sensibilidade_coortes'];table(sens.loc[sens.grupo.isin(['0','3 ou mais']),['coorte','variavel','grupo','n','percentual']],[155,115,65,75,89])
    p('Comparação das bases: com e sem as linhas NO (C1)','Heading2');p(paragraphs[8])
    # [IA] Claude – gráfico C1 no relatório, com as notas do grupo
    if 'C1' in figures:image('C1',280);p('O que mostra: '+TG.C1_NOTA['o_que_mostra']);p('Escolha visual: '+TG.C1_NOTA['escolha_visual'])
    h('9. Storytelling e escolhas visuais');p(story['percurso']);p(story['mensagem']);p(story['visuais'])
    for key in ['E1','E2','E3','E4','X1','X2']:
        story_flow.append(PageBreak());h(f'{key}. {notes[key]["titulo"]}');p('Exploratória' if key.startswith('E') else 'Explanatória - contraste identificado na exploração','Heading2');image(key,350);note(key)
    story_flow.append(PageBreak());h('10. Notas complementares e catálogo')
    for key in ['I1','A2']+[f'A2_{i}' for i in range(1,6)]:
        p(key+' - '+notes[key]['titulo'],'Heading2');note(key)
    h('11. Evidências por requisito');table(catalog[['id','criterio','evidencia','onde_encontrar']],[35,110,174,180]);p('O catálogo registra materiais disponíveis, sem estimar nota. Os critérios da Parte Específica somam 6,0 pontos, e a avaliação acadêmica cabe à docente.')
    h('12. Limitações e referências');p(story['limites']);p('[1] Clore et al. (2014). Diabetes 130-US Hospitals for Years 1999-2008. UCI. DOI 10.24432/C5230J. '+SOURCE_URL);p('[2] Strack et al. (2014). Impact of HbA1c Measurement on Hospital Readmission Rates. DOI 10.1155/2014/781670. '+PAPER_URL)
    h('Declaração de uso de IA');p(TG.DECLARACAO_IA)
    p('Rastreabilidade: o arquivo resumo.json registra o SHA-256 do CSV de origem; validacao.json registra as verificações locais. A explicação do código e o README acompanham este relatório.')
    def footer(canvas,doc):
        canvas.setFont('AVD',8);canvas.setFillColor(colors.HexColor('#627d90'));canvas.drawString(48,25,'Projeto AVD | Diabetes | Parte Específica');canvas.drawRightString(547,25,str(doc.page))
    doc=SimpleDocTemplate(str(path),pagesize=(595.28,841.89),rightMargin=48,leftMargin=48,topMargin=42,bottomMargin=45,title='Diabetes e reinternação hospitalar - Parte Específica',author='Projeto AVD')
    doc.build(story_flow,onFirstPage=footer,onLaterPages=footer)


if __name__=='__main__':
    from analise import run_analysis
    from figuras import create_figures
    raw,df,tables,summary=run_analysis()
    figs=create_figures(raw,df,tables)
    create_documents(raw,df,tables,summary,figs)
    print('Relatório PDF, explicações e catálogo gerados.')
