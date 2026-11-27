"""[IA] Claude – rascunho dos textos analíticos (hipóteses e notas dos gráficos).

Redigido com IA a partir das tabelas calculadas pelo notebook; declarado na seção "Declaração de uso de IA".

Todos os números citados se referem à base principal (REMOVER_NO = False):
101.766 internações, 71.518 pacientes e 11.357 reinternações em menos de 30 dias (11,16%).
Os textos são em texto simples, sem Markdown, porque também vão para o relatório PDF.
"""

# ---------------------------------------------------------------- pergunta
PERGUNTA = ('Quanto mais vezes o paciente foi internado no ano anterior, e quanto mais vezes foi à emergência, '
            'maior a chance de voltar ao hospital em menos de 30 dias? Isso vale para cada um separadamente e para os '
            'dois combinados? E o padrão se mantém quando olhamos só os pacientes que foram reinternados em algum momento?')

PERGUNTA_PARTES = [
    ('Cada histórico separadamente',
     'Quanto maior o número de internações no ano anterior (0, 1, 2, 3 ou mais), maior a taxa de reinternação em menos de 30 dias? E quanto maior o número de idas à emergência?',
     'X1 e X2'),
    ('Os dois históricos combinados',
     'Quando o paciente tem as duas coisas ao mesmo tempo, internações e emergências, o risco é ainda maior?',
     'M2'),
    ('Só quem voltou ao hospital',
     'Esses padrões se mantêm quando olhamos apenas os pacientes que foram reinternados em algum momento (sem as linhas NO)?',
     'C1'),
]

# ---------------------------------------------------------------- seção 5: qualidade e ausências
QUALIDADE = ('A auditoria não encontrou linhas inteiramente duplicadas nem encounter_id repetido: cada linha é uma internação única. '
             'Há 30.248 linhas de pacientes que já aparecem em outra internação (71.518 pacientes para 101.766 internações). '
             'Isso não é erro, é a própria estrutura da base, e por isso essas linhas foram mantidas. A repetição de pacientes é avaliada '
             'na análise de sensibilidade da seção 8. Os domínios numéricos estão dentro do esperado (permanência entre 1 e 14 dias, '
             'contagens inteiras e não negativas). Os códigos de diagnóstico com formato fora do padrão ICD-9 (2.646 em diag_1, 1.560 em diag_2 e 1.526 em diag_3) são códigos de 1 ou 2 dígitos, como "38" e "8", que parecem ter perdido o zero à esquerda ("038" é septicemia). Eles foram apenas sinalizados: '
             'o formato sozinho não permite afirmar que o diagnóstico esteja errado.')

AUSENCIA_TEXTO = ('A base tem quatro tipos de informação faltante, e cada um foi tratado de forma diferente: o marcador "?" (falta de registro), '
                  'a categoria Unknown/Invalid em gender (3 internações), os códigos administrativos que significam "sem informação" '
                  '(por exemplo, admission_type_id 5, 6 e 8, que somam 10,2%) e o valor None nos exames de HbA1c e glicose. '
                  'O None não é falta de dado: indica que o exame não foi feito. As ausências mais graves estão em weight (96,9%), '
                  'medical_specialty (49,1%) e payer_code (39,6%). Em race (2,2%) e nos diagnósticos (até 1,4%) elas são pequenas.')

AUSENCIA_HIPOTESES = [
    ('weight (96,9%)',
     'Hipótese: o peso não era coletado de forma rotineira no sistema de origem. A falta depende do processo de registro, e não do paciente. '
     'A proporção de ausentes é quase igual nos três desfechos (95,8% a 97,6%) e em todas as faixas etárias, por isso a ausência pouco informa sobre a reinternação. '
     'Decisão: não imputar e não usar o peso como medida, porque restam só 3.197 registros com valor.'),
    ('medical_specialty (49,1%)',
     'Hipótese: ausência dependente de outras variáveis (MAR). A falta cresce com a idade (17,4% de 0 a 10 anos e 52,3% de 80 a 90) '
     'e é um pouco menor entre quem não foi reinternado (47,3%, contra 50,9% em <30). Provavelmente reflete o tipo de admissão e a rotina de cada hospital. '
     'Decisão: manter as linhas e usar "Não informado" como categoria explícita, para não perder metade da base.'),
    ('payer_code (39,6%)',
     'Hipótese: MAR ligado à idade e ao tipo de cobertura. A falta é de 91,3% entre 0 e 10 anos e cai para 28,4% acima de 90 anos, '
     'o que é coerente com a cobertura pública dos mais velhos (Medicare, código MC, é o pagador mais frequente da base). Quase não varia entre os desfechos (38,9% a 40,7%). '
     'Decisão: manter como "Não informado".'),
    ('race (2,2%)',
     'Hipótese: falha de registro no cadastro. A falta é um pouco maior entre quem não foi reinternado (2,8%, contra 1,7% em <30). '
     'Como o volume é pequeno, a categoria "Não informado" foi mantida.'),
    ('diag_1, diag_2 e diag_3 (0,02% a 1,4%)',
     'Hipótese: ausência estrutural. O diagnóstico secundário ou adicional falta quando o paciente teve menos diagnósticos registrados. '
     'O mapa de calor mostra que, das 358 internações sem diag_2, 279 também não têm diag_3. '
     'Decisão: manter e tratar como "Não informado", sem inventar diagnóstico.'),
    ('A1Cresult (83,3%) e max_glu_serum (94,7%) = None',
     'Não é ausência: o exame não foi feito, e isso tem significado clínico (é a pergunta do artigo original). '
     'Decisão: manter None como categoria própria.'),
    ('Ausências conjuntas',
     'Os mapas de calor mostram que as ausências não se concentram nas mesmas internações. Sem payer_code, 40,6% não têm especialidade, '
     'e com payer_code, 54,6% não têm. Isso afasta a ideia de um "bloco" de registros incompletos, que poderia ser excluído de uma só vez.'),
]

AUSENCIA_RESSALVA = ('Os dados permitem verificar só se a falta muda com variáveis observadas (idade e desfecho). Não é possível provar MCAR, MAR ou MNAR, '
                     'por isso as classificações acima são hipóteses. Em todos os casos, a decisão foi preservar as linhas, para não mudar a composição da base.')


def ausencia_texto_simples():
    """Hipóteses em texto corrido (PDF e relatório Markdown)."""
    linhas = [f'{a}: {t}' for a, t in AUSENCIA_HIPOTESES]
    return '\n\n'.join(linhas + [AUSENCIA_RESSALVA])


def ausencia_markdown():
    """Hipóteses em lista (notebook e dashboard)."""
    linhas = [f'- **{a}:** {t}' for a, t in AUSENCIA_HIPOTESES]
    return '#### Hipóteses de ausência e tratamento\n\n' + '\n'.join(linhas) + '\n\n' + AUSENCIA_RESSALVA


# ---------------------------------------------------------------- seção 4: skewness e kurtosis
ASSIMETRIA = [
    ('Emergências prévias', 'skewness 22,86 e kurtosis 1.191,7', 'a distribuição mais extrema da base. 88,8% das internações têm zero emergências, e poucos pacientes chegam a dezenas (máximo de 76). A média (0,20) não representa o paciente típico.'),
    ('Consultas ambulatoriais prévias', 'skewness 8,83 e kurtosis 147,9', 'mesmo padrão: 83,6% de zeros e uma cauda longa à direita (máximo de 42).'),
    ('Internações prévias', 'skewness 3,61 e kurtosis 20,7', 'assimetria forte, mas menor. 66,5% não tiveram internação no ano anterior, e a cauda chega a 21. É a variável central da pergunta, por isso foi agrupada em 0, 1, 2 e 3 ou mais.'),
    ('Medicamentos', 'skewness 1,33 e kurtosis 3,47', 'assimetria moderada à direita, com mediana de 15 e alguns casos acima de 35.'),
    ('Permanência e procedimentos', 'skewness 1,13 e 1,32; kurtosis 0,85 e 0,86', 'assimetria moderada e caudas leves. Os valores são limitados pelo próprio domínio (1 a 14 dias e 0 a 6 procedimentos).'),
    ('Exames laboratoriais', 'skewness -0,24 e kurtosis -0,25', 'quase simétrica, com média (43,1) e mediana (44) próximas.'),
    ('Diagnósticos', 'skewness -0,88 e kurtosis -0,08', 'assimetria à esquerda: os valores se acumulam no teto de 9 diagnósticos (48,6% das internações), e só 0,1% passa disso.'),
]
ASSIMETRIA_CONCLUSAO = ('A kurtosis apresentada é o excesso de curtose (o valor da normal é 0). Nas três contagens de histórico, '
                        'a média é puxada pela cauda, então descrevemos essas variáveis por mediana, percentis e grupos. '
                        'Os coeficientes de Spearman foram mantidos ao lado dos de Pearson porque não dependem da forma da distribuição.')


def assimetria_texto_simples():
    return '\n\n'.join([f'{v} ({n}): {t}' for v, n, t in ASSIMETRIA] + [ASSIMETRIA_CONCLUSAO])


def assimetria_markdown():
    linhas = [f'- **{v}** ({n}): {t}' for v, n, t in ASSIMETRIA]
    return '#### Assimetria (skewness) e curtose (kurtosis)\n\n' + '\n'.join(linhas) + '\n\n' + ASSIMETRIA_CONCLUSAO


# ---------------------------------------------------------------- seção 6: outliers
OUTLIERS = ('A regra do IQR sinaliza 45.358 ocorrências somando os oito atributos (a mesma internação pode ser contada mais de uma vez). '
            'Nas consultas ambulatoriais e nas emergências o IQR é zero, porque mais da metade das internações tem valor 0, '
            'e qualquer valor positivo vira "outlier" (16,4% e 11,2% das linhas). Em internações prévias o limite superior é 2,5. '
            'Assim, todo paciente com 3 ou mais internações seria sinalizado (6,9%), e esse é justamente o grupo com a maior taxa de reinternação '
            'em menos de 30 dias (25,7%). Remover esses casos apagaria o contraste que a pergunta quer estudar. Os valores também são plausíveis: '
            'a permanência fica entre 1 e 14 dias, e contagens altas de emergência correspondem a pacientes que usam muito o serviço. '
            'Decisão: preservar todos os valores e usar o IQR apenas como triagem.')

EXTREMOS_SIMULTANEOS = {
    'o_que_mostra': ('Tabela cruzada e mapa de calor das internações que passam do limite superior do IQR em medicamentos (mais de 35) '
                     'e em internações prévias (mais de 2,5, ou seja, 3 ou mais). Só 118 internações são extremas nas duas variáveis ao mesmo tempo.'),
    'interpretacao': ('Os extremos não aparecem juntos. Entre as internações com muitos medicamentos, 4,6% também têm 3 ou mais internações prévias, '
                      'contra 7,0% nas demais. Se os extremos fossem erro sistemático de digitação ou de carga, esperaríamos que se acumulassem nas mesmas linhas. '
                      'Eles também se comportam de forma diferente em relação ao desfecho. A taxa de reinternação em menos de 30 dias é de 25,7% '
                      'quando só o histórico é extremo, 11,5% quando só os medicamentos são extremos e 10,0% quando nenhum é. '
                      'O histórico extremo carrega informação, por isso foi mantido.'),
    'escolha_visual': ('Tabela 2 × 2 com contagens absolutas no mapa de calor, para mostrar de imediato onde estão as internações. '
                       'A escala magma deixa a célula grande (nenhum extremo) escura e realça as células pequenas. '
                       'Os limites usados estão escritos nos rótulos dos eixos.'),
}

# ---------------------------------------------------------------- seção 7: distribuições
DISTRIBUICAO = ('As distribuições mostram uma base concentrada em pacientes idosos (47,7% entre 60 e 80 anos) e mulheres (53,8%), '
                'com internações curtas (mediana de 4 dias) e cerca de 15 medicamentos. As contagens de histórico têm muitos zeros. '
                'Nas variáveis categóricas, a maior parte dos 23 medicamentos quase não varia (mais de 99% "No" em vários deles, '
                'e examide e citoglipton têm uma única categoria). Os exames HbA1c e glicose quase sempre aparecem como "não realizados". '
                'O desfecho se divide em 53,9% NO, 34,9% >30 e 11,2% <30: a classe de interesse é minoritária, por isso comparamos proporções e não contagens absolutas.')

# ---------------------------------------------------------------- notas dos gráficos (o_que_mostra, interpretacao, escolha_visual)
# None mantém o texto que já existia no código.
NOTAS = {
    'Q1': ('Contagem de registros faltantes por atributo, separada por tipo: marcador "?", Unknown/Invalid, código administrativo sem informação e None nos exames.',
           'O peso falta em quase toda a base (98.569 registros). Especialidade e pagador faltam em cerca de metade e 40% das internações. '
           'O None de HbA1c e glicose é o segundo maior volume, mas significa exame não feito, e não dado perdido. Os demais faltantes são pequenos.',
           'Barras horizontais ordenadas da maior para a menor, para ler os nomes dos atributos sem girar o texto. '
           'A ordenação cria uma hierarquia visual: o olho começa pelo atributo mais crítico (weight, que falta em quase toda a base) e desce até os menores, sem precisar comparar barras espalhadas. '
           'A cor separa o tipo de faltante, porque cada tipo recebe tratamento diferente. Os rótulos trazem a contagem exata.'),
    'Q2': ('Um boxplot para cada uma das oito variáveis numéricas, usando todas as internações. Os pontos isolados são os valores além dos limites do IQR.',
           'Em consultas ambulatoriais, emergências e internações prévias, quase todos os pontos acima da caixa são contagens plausíveis de uso do serviço, e não erros. '
           'Nas emergências, a caixa vira uma linha no zero. Permanência e procedimentos ficam presos aos limites do domínio. '
           'Exames laboratoriais têm alguns valores acima de 96, mas são poucos (0,14%).',
           'Escolhemos o boxplot porque ele mostra diretamente a mediana, os quartis e os pontos que a regra do IQR sinaliza. Cada variável tem seu próprio painel e sua própria escala, porque os intervalos são muito diferentes (0 a 6 procedimentos e até 132 exames).'),
    'E1': ('Número de internações por faixa etária de dez anos, com a parte de reinternações em menos de 30 dias empilhada em laranja.',
           'A base é de pacientes mais velhos: 25,6% das internações estão entre 70 e 80 anos e 81,6% entre 50 e 90. '
           'A fatia laranja acompanha o tamanho de cada faixa. A taxa fica entre 9,7% e 12,1% dos 30 aos 100 anos, com pico de 14,2% entre 20 e 30 anos, '
           'uma faixa pequena (1.657 internações). A idade, sozinha, não separa bem quem volta rápido.',
           'Barras empilhadas em duas cores mostram o volume de cada faixa e, ao mesmo tempo, a parte que volta em menos de 30 dias. '
           'O eixo x segue a ordem natural das faixas, e o laranja é a cor do desfecho de interesse em todo o projeto.'),
    'E2': ('Boxplot da permanência hospitalar em dias para cada desfecho: sem reinternação registrada, após 30 dias e em menos de 30 dias.',
           'As medianas são quase iguais: 4 dias para <30 e >30 e 3 dias para quem não foi reinternado. As caixas se sobrepõem bastante. '
           'A média é um pouco maior em <30 (4,77 dias, contra 4,35 nas demais). A permanência tem relação fraca com a reinternação rápida e não diferencia os grupos tão bem quanto o histórico.',
           'Os três boxplots ficam lado a lado e na mesma escala, para comparar mediana e dispersão. Cada caixa usa a cor do seu desfecho, a mesma dos outros gráficos.'),
    'E3': ('Distribuição do número de medicamentos por internação em três painéis, um por desfecho, com a curva de densidade (KDE) em vermelho na escala de contagem.',
           'As três distribuições têm a mesma forma: assimétricas à direita, com pico entre 10 e 20 medicamentos e cauda até cerca de 80. '
           'A mediana sobe pouco de NO (14) para >30 (15) e <30 (16). Como as alturas refletem o tamanho de cada grupo, o que importa comparar é a forma, e ela quase não muda.',
           'Um painel por desfecho evita sobrepor barras de grupos com tamanhos muito diferentes. A cor de cada painel é a cor do desfecho, '
           'e a KDE em vermelho contrasta com as barras para destacar a forma. O eixo x é o mesmo (0 a 85) nos três painéis.'),
    'E4': ('Quatro matrizes de correlação entre as oito variáveis numéricas: Pearson e Spearman, calculadas separadamente para <30 dias e para as demais categorias.',
           'Nenhuma correlação é forte. A maior é entre permanência e medicamentos (0,46 a 0,48). A diferença mais interessante está entre internações e emergências prévias: '
           'a correlação é de 0,32 (Pearson) no grupo <30 e de 0,24 nas demais. Entre quem volta rápido, os dois históricos andam mais juntos, o que motivou o cruzamento M2. '
           'Pearson e Spearman dão resultados parecidos, então as conclusões não dependem dos extremos.',
           'Mapa de calor com escala divergente fixa de -1 a 1 (azul negativo, vermelho positivo), igual nos quatro painéis, para que as cores sejam comparáveis. '
           'Os valores aparecem em cada célula, porque as diferenças são pequenas.'),
    'H1': ('Histogramas de permanência, exames laboratoriais, procedimentos e medicamentos, com um painel para cada desfecho.',
           'As formas são parecidas nos três desfechos. As diferenças de altura vêm principalmente do tamanho dos grupos (NO é cerca de cinco vezes maior que <30). '
           'Nenhuma dessas quatro variáveis do período da internação mostra um deslocamento claro no grupo <30.',
           'Grade de linhas (variáveis) por colunas (desfechos), com eixo x compartilhado em cada linha. Assim, a comparação entre desfechos é feita na mesma escala horizontal. '
           'As cores são as mesmas dos demais gráficos.'),
    'H2': ('Histogramas de consultas ambulatoriais, emergências, internações prévias e diagnósticos, com um painel para cada desfecho.',
           'As três contagens de histórico se concentram no zero, mas a cauda das internações prévias é proporcionalmente mais pesada em <30: '
           '49,8% desse grupo teve ao menos uma internação no ano anterior, contra 24,2% em NO. Os diagnósticos se acumulam no valor 9 em todos os desfechos.',
           'Mesma grade do H1, para manter a leitura consistente. Barras espaçadas deixam claro que as variáveis são contagens discretas.'),
    'A1': ('Distribuição acumulada empírica (ECDF) das oito variáveis numéricas: para cada valor, a proporção de internações com valor menor ou igual a ele.',
           'As curvas de histórico sobem quase até o topo no zero: 66,5% das internações não tiveram internação prévia, 88,8% não tiveram emergência e 83,6% não tiveram consulta ambulatorial. '
           'Medicamentos e exames sobem de forma gradual. Cerca de 76% das internações usam até 20 medicamentos.',
           'A ECDF mostra a distribuição inteira sem escolher número de classes e permite ler percentis diretamente no eixo y. '
           'Uma curva por painel evita misturar escalas diferentes.'),
    'A2': ('Frequência de todas as 40 variáveis categóricas (incluindo o desfecho), distribuídas em cinco páginas.',
           'Muitas variáveis de medicamento são quase constantes, e várias categóricas são dominadas por uma única categoria ou por "Não informado". '
           'Essas variáveis dão pouca informação para separar os desfechos. '
           'As categorias raras, com poucos registros, também seriam um problema para um modelo de machine learning: ele veria poucos exemplos delas e tenderia a aprender ruído. '
           'Numa modelagem futura, o caminho seria agrupar as categorias raras em "Outras" e descartar as variáveis quase constantes.',
           'Barras verticais com as sete categorias mais frequentes e o restante agregado em "Outras", só na apresentação. A tabela completa fica no CSV.'),
    'A2_1': ('Frequências de race, gender, age, weight, admission_type_id, discharge_disposition_id, admission_source_id e payer_code.',
             'Predominam pacientes Caucasian (74,8%) e mulheres (53,8%). O peso é "Não informado" em 96,9% dos casos. '
             'A admissão de emergência (código 1) responde por 53,1% e a alta para casa (código 1) por 59,2%. Em payer_code, "Não informado" (39,6%) supera o Medicare (31,9%).',
             'Barras verticais ordenadas por frequência. Os códigos administrativos aparecem como categorias, e não como números, porque são nominais.'),
    'A2_2': ('Frequências de medical_specialty, diag_1, diag_2, diag_3, max_glu_serum, A1Cresult, metformin e repaglinide.',
             'A especialidade mais comum é "Não informado" (49,1%), seguida de medicina interna (14,4%). Os diagnósticos têm centenas de códigos, e o mais frequente (428, insuficiência cardíaca) não passa de 7%. '
             'Glicose e HbA1c não foram medidas em 94,7% e 83,3% das internações. A metformina é usada em cerca de 20%.',
             'A agregação em "Outras" é necessária para os diagnósticos, com mais de 700 códigos cada. Sem ela o gráfico ficaria ilegível.'),
    'A2_3': ('Frequências de nateglinide, chlorpropamide, glimepiride, acetohexamide, glipizide, glyburide, tolbutamide e pioglitazone.',
             'Quase todos os registros são "No". Glipizide (11,2% Steady) e glyburide (9,1%) são os mais usados nesta página. '
             'Acetohexamide e tolbutamide praticamente não aparecem.',
             'Mesmo formato das outras páginas, para facilitar a comparação. O eixo y em contagem deixa evidente a dominância do "No".'),
    'A2_4': ('Frequências de rosiglitazone, acarbose, miglitol, troglitazone, tolazamide, examide, citoglipton e insulin.',
             'A insulina é a exceção: só 46,6% "No", com 30,3% Steady, 12,0% Down e 11,1% Up. Examide e citoglipton têm uma única categoria em toda a base, '
             'e as outras ficam próximas de 100% "No".',
             'Mesmo formato das outras páginas. Variáveis constantes foram mantidas no gráfico, para documentar que foram verificadas.'),
    'A2_5': ('Frequências das combinações de medicamentos, de change, de diabetesMed e do desfecho readmitted.',
             'As combinações são raríssimas. Houve mudança na medicação de diabetes em 46,2% das internações, e 77,0% receberam algum medicamento para diabetes. '
             'O desfecho se divide em 53,9% NO, 34,9% >30 e 11,2% <30.',
             'Mesmo formato das outras páginas. A página termina com o desfecho, que serve de referência para todas as proporções do projeto.'),
    'M1': ('Mapa de calor em que as linhas são faixas etárias e as colunas são grupos de internações prévias (0, 1, 2, 3 ou mais). Cada célula mostra a porcentagem de reinternação em menos de 30 dias e o número de internações (n).',
           'Na base integral: em quase todas as faixas etárias, a taxa sobe da esquerda para a direita, de 0 até 3 ou mais internações prévias. Entre 70 e 80 anos, por exemplo, vai de 9,6% para 23,5%. '
           'O efeito do histórico não é explicado pela idade. As células mais escuras (41,6% entre 20 e 30 anos com 3 ou mais) têm denominadores pequenos e devem ser lidas com cautela.',
           'A escala de cor é fixa de 0 a 100%, para que a mesma cor signifique a mesma taxa em qualquer recorte. O n aparece em cada célula para que uma célula escura com poucos casos não seja lida como resultado forte.'),
    'M2': ('Mapa de calor em que as linhas são os grupos de internações prévias e as colunas os grupos de emergências prévias. Cada célula mostra a porcentagem de reinternação em menos de 30 dias e o n.',
           'Na base integral: os dois históricos somam risco. Quem não teve internação nem emergência no ano anterior volta em menos de 30 dias em 8,3% dos casos. '
           'Com 3 ou mais internações e 3 ou mais emergências, a taxa é de 33,4% (n=752), quatro vezes maior. As internações prévias pesam mais: '
           'sem nenhuma emergência, a taxa já vai de 8,3% para 23,4% quando as internações passam de 0 para 3 ou mais. As emergências acrescentam um efeito menor e menos regular '
           '(na linha de 2 internações, a taxa oscila entre 15,2% e 20,5%).',
           'Usamos o mesmo formato e a mesma escala fixa do M1. Cruzar os dois históricos numa única grade permite ver se o risco aumenta quando o paciente tem os dois ao mesmo tempo. O n em cada célula indica onde os grupos são pequenos.'),
    'I1': ('Gráfico de dispersão de duas variáveis numéricas escolhidas no painel, com cor por desfecho. Usa uma amostra de até 4.000 internações.',
           'O gráfico serve para o leitor formular as próprias perguntas no painel. Na maioria dos pares de variáveis, as cores dos desfechos se misturam, '
           'o que confirma que nenhuma variável numérica, sozinha, separa quem volta em menos de 30 dias.',
           'Os pontos são semitransparentes para que as áreas com muitas internações apareçam mais escuras. Os eixos podem ser escolhidos no painel para que o leitor teste outras combinações.'),
    'X1': ('Porcentagem de internações que voltaram em menos de 30 dias em cada grupo de internações prévias no ano anterior (0, 1, 2, 3 ou mais), com o n de cada grupo acima da barra.',
           'Na base integral: a taxa de reinternação em menos de 30 dias sobe a cada degrau do histórico de internações: 8,4% sem internação prévia, 12,9% com 1, 17,4% com 2 e 25,7% com 3 ou mais. '
           'O último grupo tem uma taxa três vezes maior que o primeiro (diferença de 17,2 pontos percentuais), com 7.049 internações no denominador.',
           'As barras começam em zero para que a altura seja proporcional à taxa. Só o grupo de 3 ou mais aparece em laranja, porque é a mensagem principal; os outros ficam em cinza. A escala vertical é a mesma do X2, para comparar os dois históricos.'),
    'X2': ('Porcentagem de internações que voltaram em menos de 30 dias em cada grupo de emergências prévias no ano anterior (0, 1, 2, 3 ou mais), com o n de cada grupo acima da barra.',
           'Na base integral: o mesmo padrão aparece nas emergências: 10,5% sem emergência prévia, 14,4% com 1, 18,3% com 2 e 24,9% com 3 ou mais (diferença de 14,5 pontos). '
           'O grupo de 3 ou mais é pequeno (1.664 internações), e 88,8% da base não teve nenhuma emergência no ano anterior.',
           'Mesmo desenho do X1 (eixo em zero, destaque em laranja no 3 ou mais e mesma escala vertical), para que as duas figuras sejam lidas como um par.'),
}

# ---------------------------------------------------------------- seção 8: comparação C1
C1_INTRO = ('A base principal segue o artigo original: compara quem voltou em menos de 30 dias com todos os demais, que reúnem quem voltou depois de 30 dias (>30) '
            'e quem não tem reinternação registrada (NO). Para responder à terceira parte da pergunta, refizemos as taxas só com os pacientes que voltaram ao hospital '
            'em algum momento, retirando as linhas NO. Nessa base de 46.902 internações, a pergunta passa a ser: entre quem volta, quem volta mais rápido? '
            'A taxa geral sobe para 24,2%, porque o denominador fica menor. Por isso, o que interessa comparar é a inclinação entre os grupos, e não o nível das barras.')

C1_NOTA = {
    'o_que_mostra': ('Taxa de reinternação em menos de 30 dias por grupo de histórico (0, 1, 2 e 3 ou mais), nas duas bases lado a lado: '
                     'todas as internações (com NO) e somente reinternados (sem NO). O painel da esquerda mostra internações prévias e o da direita, emergências prévias.'),
    'interpretacao': ('O padrão se mantém nas duas bases: quanto maior o histórico, maior a taxa. Nas internações prévias, a taxa vai de 8,4% a 25,7% com NO e de 21,9% a 34,4% sem NO. '
                      'Nas emergências, vai de 10,5% a 24,9% com NO e de 23,9% a 31,8% sem NO. A inclinação, porém, cai bastante. Com NO, o grupo de 3 ou mais tem uma taxa três vezes maior que o grupo sem histórico. '
                      'Sem NO, a taxa é só 1,6 vez maior nas internações e 1,3 vez nas emergências, e os grupos 0 e 1 de emergência ficam quase iguais (23,9% e 24,2%). '
                      'Boa parte do efeito do histórico está em separar quem volta de quem não volta: 42,8% do grupo >30 também teve internação prévia. '
                      'Mesmo entre os que voltam, o histórico continua indicando quem volta mais cedo.'),
    'escolha_visual': ('Barras agrupadas com a mesma escala vertical nos dois painéis, para comparar diretamente a altura e a inclinação. '
                       'Cinza para a base com NO, que é a referência, e azul-petróleo para o recorte. Cada barra mostra o percentual e o n, para que o leitor veja que os grupos sem NO são menores.'),
}

# ---------------------------------------------------------------- seção 9: storytelling
STORY = {
    'publico': ('Gestores de qualidade hospitalar e analistas de dados que precisam decidir quais pacientes devem receber acompanhamento depois da alta. '
                'O texto evita jargão estatístico e sempre mostra o denominador de cada taxa.'),
    'percurso': ('O percurso segue a ordem da investigação. Primeiro verificamos se a base era confiável: duplicatas, ausências e extremos. Nessa etapa vimos que os "outliers" de histórico eram justamente '
                 'o grupo de maior risco e decidimos preservá-los. Depois olhamos as distribuições (E1 a E3) e as correlações (E4), que mostraram que as variáveis do período da internação, como permanência, '
                 'medicamentos e exames, quase não diferenciam os desfechos. A diferença apareceu no histórico de uso do hospital. Então comparamos as proporções por grupo de histórico (X1 e X2), '
                 'cruzamos os dois históricos e a idade (M1 e M2), testamos a robustez em outras coortes e, por fim, repetimos a análise sem as linhas NO (C1).'),
    'resposta': ('Sim, nas três partes da pergunta. (1) Separadamente: a taxa de reinternação em menos de 30 dias sobe de 8,4% para 25,7% conforme aumentam as internações prévias '
                 'e de 10,5% para 24,9% conforme aumentam as emergências prévias. (2) Combinados: quem tem 3 ou mais internações e 3 ou mais emergências volta em 33,4% dos casos, '
                 'quatro vezes mais que quem não tem nenhum dos dois históricos (8,3%). As internações prévias pesam mais que as emergências. (3) Só entre os reinternados: o padrão se mantém, mas mais fraco. '
                 'As taxas vão de 21,9% a 34,4% por internações e de 23,9% a 31,8% por emergências. O histórico indica não só se o paciente volta, mas também se volta rápido. '
                 'Para as internações prévias, o resultado também se sustenta com uma linha por paciente e sem as altas por óbito ou hospice: com 3 ou mais internações, a taxa fica entre 25,8% e 26,5%.'),
    'mensagem': ('O passado hospitalar é o sinal mais claro de reinternação rápida nesta base. Um paciente que esteve internado três ou mais vezes no ano anterior tem cerca de '
                 'uma chance em quatro de voltar antes de completar um mês da alta. Para quem não teve internação, a chance é de uma em doze. Essa informação já está disponível no momento da admissão.'),
    'visuais': ('Os gráficos E1 a E4 são exploratórios, usados para entender o comportamento dos dados, e X1 e X2 são explanatórios, usados para comunicar o achado. '
                'O X1 responde diretamente à pergunta de pesquisa. '
                'E1: o gráfico de barras empilhadas foi escolhido porque permite visualizar, simultaneamente, o volume total de internações em cada faixa etária '
                'e a composição interna de cada grupo segundo o desfecho de reinternação. '
                'E2: o tamanho da caixa revela em qual desfecho o tempo é mais previsível ou mais espalhado, comparando o padrão de quem volta após 30 dias ou quem volta antes de 30 dias. '
                'A única diferença visual ocorre na linha da mediana: quem não registra reinternação tem mediana de 3 dias, enquanto quem retorna '
                '(tanto após 30 dias quanto em menos de 30 dias) apresenta mediana ligeiramente maior, de 4 dias. '
                'E3: o histograma com a curva de densidade (KDE) é excelente para mostrar onde está o pico de consumo e a forma da distribuição, revelando a assimetria dos dados apresentados. '
                'Aplicado ao número de medicamentos diferentes administrados durante a internação, o gráfico mostra que, nos três cenários, os dados apresentam forte assimetria '
                'com cauda longa à direita e um pico concentrado na mesma faixa, entre 12 e 15 medicamentos. '
                'E4: o mapa de calor foi adotado porque permite visualizar simultaneamente todos os 28 pares possíveis entre as 8 variáveis analisadas, algo que seria ilegível '
                'em gráficos de dispersão individuais ou tabelas extensas. Além disso, a cor indica a força e o sinal da correlação, numa escala de −1 a 1. '
                'X1 e X2 usam barras com eixo começando em zero e a mesma escala vertical, para que a altura seja comparável entre os dois históricos. '
                'O laranja destaca só o grupo de 3 ou mais, que é a mensagem principal; os demais ficam em cinza (atributo pré-atentivo de cor). '
                'Cada barra traz o percentual e o n, para que o leitor não confunda um grupo pequeno com um grupo grande. M1 e M2 usam mapa de calor com escala fixa de 0 a 100% '
                'e o denominador em cada célula. O C1 coloca as duas bases lado a lado na mesma escala, para que a mudança de inclinação seja vista de imediato. '
                'Não foi necessário o uso de gráfico de pizza ou de radar.'),
    'limites': ('Os resultados são descritivos e não provam causa: o histórico pode estar indicando gravidade ou condições crônicas que não estão na base. '
                'Um mesmo paciente pode aparecer em várias internações, e por isso não aplicamos testes de significância que suponham independência. '
                'NO significa ausência de registro de reinternação nesta rede de hospitais, e não garantia de que o paciente não voltou a outro serviço. '
                'Os dados são de 1999 a 2008, de hospitais dos Estados Unidos, e não devem ser generalizados para outros contextos sem cautela. '
                'Os grupos de 3 ou mais emergências e algumas células de M1 e M2 têm denominadores pequenos. Com uma linha por paciente, a taxa no grupo de 3 ou mais emergências cai de 24,9% para 16,1% (435 pacientes): o efeito das emergências depende mais de pacientes que se repetem na base do que o das internações.'),
}


# ---------------------------------------------------------------- declaração de uso de IA
DECLARACAO_IA = (
    'Ferramenta utilizada: Claude (Anthropic), usado como assistente de código e de redação. '
    'O que foi gerado com IA na Parte Específica: (1) os trechos de código marcados com "[IA] Claude": tabelas auxiliares, ajustes de gráficos, '
    'heatmaps de ausência, extremos simultâneos e a comparação C1; (2) a redação dos textos analíticos (src/parte_especifica/textos_grupo.py), '
    'incluindo as notas de cada gráfico. O grupo revisou os textos e conferiu os números citados. '
    'O que foi decidido e feito pelo grupo: o dataset original tratava do absenteísmo no trabalho. No entanto, a professora reenviou o e-mail '
    'a um dos membros, detalhando alguns problemas que o dataset poderia apresentar, como o pequeno número de pessoas, o que resultaria em '
    'variáveis repetidas em várias instâncias. Diante disso, outro membro sugeriu um dataset substituto, sobre diabetes. As perguntas foram '
    'formuladas de modo a não seguir um único caminho: a análise segue direções diferentes conforme os valores encontrados e as condições '
    'necessárias para chegar a cada resultado. '
    'Verificação: todos os números citados podem ser reproduzidos executando o notebook. O grupo revisou os resultados e se responsabiliza '
    'pelo conteúdo entregue. Todos os integrantes sabem explicar cada parte do trabalho. '
    'A declaração completa, que também cobre a Parte Comum e traz as assinaturas, está em docs/DECLARACAO_IA.pdf.')
