"""Pergunta, decisões e notas aprovadas na revisão dos gráficos."""
PERGUNTA = 'Como a proporção de reinternações registradas em menos de 30 dias varia conforme a duração da internação?'
PUBLICO = 'Turma e professora de Análise e Visualização de Dados.'

FIGURAS = {
    'q1': {
        'titulo': 'Q1. Preenchimento da base',
        'finalidade': 'Exploratória',
        'mostra': 'Quantas internações têm informação ausente ou inválida em cada coluna da base original. O painel ao lado conta exames que ficaram registrados como não medidos.',
        'leitura': 'Peso foi a coluna menos preenchida, com 98.569 ausências. Especialidade veio em seguida, com 49.949. Uma comparação que usa peso parte de 3.197 internações com a informação disponível.',
        'escolha': 'As barras ordenadas criam uma hierarquia e destacam as colunas com mais ocorrências. Os painéis usam a mesma escala e distinguem ausências de exames não medidos.',
        'fala': 'Conferimos o preenchimento antes da análise. O peso foi o campo menos preenchido e a especialidade veio em segundo. A ordem das barras deixa essa diferença visível.'
    },
    'peso': {
        'titulo': 'Faixas de peso em kg',
        'finalidade': 'Exploratória',
        'mostra': 'Contagem de internações nas faixas de peso preenchidas na base original. Os limites aparecem em kg.',
        'leitura': 'Entre os 3.197 registros com faixa de peso, a faixa de aproximadamente 34,02 a 45,36 kg foi a mais frequente, com 1.336 registros.',
        'escolha': 'Cada faixa é uma categoria. As barras permitem comparar quantos registros há em cada faixa e deixam os rótulos legíveis.',
        'fala': 'Usei barras porque cada faixa é uma categoria. O comprimento mostra quantas internações caíram nela. O título informa os 98.569 pesos que ficaram ausentes.'
    },
    'permanencia': {
        'titulo': 'Internações por duração',
        'finalidade': 'Exploratória',
        'mostra': 'Total de internações para cada duração, de 1 a 14 dias.',
        'leitura': 'Três dias foi a duração mais frequente, com 17.756 internações.',
        'escolha': 'As barras comparam contagens em dias inteiros. A barra mais escura e o rótulo acima dela localizam a duração mais frequente.',
        'fala': 'Três dias foi a duração que mais apareceu, com 17.756 internações. Usei barras porque queria comparar a contagem para cada número de dias.'
    },
    'caixas': {
        'titulo': 'Permanência por desfecho',
        'finalidade': 'Exploratória',
        'mostra': 'Distribuição da duração da internação para cada categoria de reinternação registrada.',
        'leitura': 'A mediana foi de três dias no grupo sem retorno registrado e de quatro dias nos dois grupos com retorno. Os 50% centrais ficam entre dois e seis dias nos três grupos.',
        'escolha': 'O boxplot mostra a mediana e a faixa entre o primeiro e o terceiro quartil na mesma escala. A linha em cor de destaque indica a mediana.',
        'fala': 'Escolhi boxplots para ler a mediana e a faixa central de cada grupo. Sem retorno registrado, a mediana foi de três dias. Nos dois grupos com retorno, foi de quatro. As três caixas vão de dois a seis dias.'
    },
    'reinternacao': {
        'titulo': 'Reinternação por dia de permanência',
        'finalidade': 'Explanatória',
        'mostra': 'Em cada duração, divide os casos registrados em menos de 30 dias pelo total de internações do grupo. O eixo horizontal traz o total usado em cada cálculo.',
        'leitura': 'A proporção foi de 14,35% entre as internações de dez dias, 10,51% entre as de 11 dias e 13,33% entre as de 12 dias. As proporções oscilam de um dia de permanência para o outro.',
        'escolha': 'Um ponto por dia mantém visíveis as oscilações. A altura mostra a proporção, as porcentagens aparecem sobre os pontos e os totais ficam abaixo dos dias.',
        'fala': 'Entre as 2.342 internações de dez dias, houve 336 retornos registrados em menos de 30 dias, o que dá 14,35%. Com 11 dias, deu 10,51%. Com 12, deu 13,33%. Mostrei cada duração para essa variação aparecer.'
    },
    'idades': {
        'titulo': 'Permanência e reinternação por faixa etária',
        'finalidade': 'Explanatória',
        'mostra': 'Proporções por duração nas duas faixas etárias mais frequentes na cópia de análise. A tabela mostra os casos e os totais de cada faixa e duração.',
        'leitura': 'Entre as internações de dez dias, foram 76 casos em 554 internações de pessoas de 60 a 69 anos (13,72%) e 103 em 645 de pessoas de 70 a 79 anos (15,97%).',
        'escolha': 'Dois símbolos e cores na mesma escala distinguem as faixas. Os pontos lado a lado permitem comparar as duas proporções para a mesma duração.',
        'fala': 'Usei as duas faixas etárias com mais internações na base. Entre as de dez dias, a proporção foi de 13,72% para 60 a 69 anos e 15,97% para 70 a 79 anos. Cada porcentagem usa o total da sua faixa para aquela duração.'
    },
}
ORDEM_FIGURAS = ['q1', 'peso', 'permanencia', 'caixas', 'reinternacao', 'idades']

RESPOSTA = (
    'As proporções de reinternação registrada diferem entre as durações e oscilam de um dia para o outro. '
    'Entre internações de dez, 11 e 12 dias, foram 14,35%, 10,51% e 13,33%. O recorte por idade permite '
    'ver também como essas proporções variam entre as duas faixas mais frequentes para a mesma duração.'
)

LIMITES = (
    'A análise compara internações, e uma pessoa pode contribuir com várias linhas. O desfecho é o que '
    'ficou registrado no conjunto de dados. As proporções descrevem grupos observados e não permitem atribuir '
    'a variação à duração da internação ou à faixa etária.'
)

TRATAMENTOS = {
    'Sexo registrado': 'A categoria desconhecida ou inválida aparece em três registros, todos sem retorno registrado. Retiramos essas linhas da cópia de análise. Passamos de 101.766 para 101.763 internações e mantivemos os mesmos 11.357 casos registrados em menos de 30 dias. O arquivo não identifica a causa da categoria inválida.',
    'Especialidade, pagador e raça': 'Mantivemos as internações e marcamos os campos vazios como Não informado. Isso permite contar quem ficou sem informação. O arquivo mostra os campos incompletos, mas não traz o processo de coleta para identificar a causa de cada ausência.',
    'Diagnósticos': 'Os códigos ausentes continuam nulos. Das 358 internações sem segundo diagnóstico, 219 tinham total menor que dois. Das 1.423 sem terceiro diagnóstico, 1.242 tinham total menor que três. A contagem ajuda a entender por que algumas posições podem estar vazias. Nos demais casos e entre os 21 sem primeiro diagnóstico, não há informação suficiente para recuperar o código.',
    'Peso': 'A base original tem 3.197 faixas preenchidas. Convertemos os limites de libras para kg e mantivemos em branco os pesos ausentes. Permanência e desfecho estão preenchidos também nessas linhas, por isso elas continuam na pesquisa principal.',
    'Admissão e alta': 'Alguns códigos significam que o campo está indisponível, desconhecido ou sem mapeamento. Conferimos o dicionário e os contamos na auditoria. Os códigos originais permanecem na cópia de análise.',
    'Exames': 'O valor None em HbA1c e glicose sérica indica que o exame não foi medido. Ele fica separado das ausências e dos resultados medidos.',
}

ASSIMETRIA = (
    'Em emergências prévias, 90.380 internações tinham zero atendimento registrado no ano anterior. '
    'O percentil 99 foi 3 e o máximo foi 76. A assimetria de 22,86 indica uma cauda longa à direita. '
    'A curtose de Fisher de 1.191,65 mostra quanto os valores extremos pesam nessa medida. '
    'A média fica em 0,20. Junto com o percentil e o máximo, ela ajuda a ver o contraste entre '
    'o volume de registros com poucas emergências e o tamanho dos valores mais altos.'
)

EXTREMOS = (
    'Para cada medida, calculamos o primeiro e o terceiro quartil e a distância entre eles (IQR). '
    'Sinalizamos valores abaixo de Q1 − 1,5 × IQR ou acima de Q3 + 1,5 × IQR. Na permanência, '
    'a regra marcou 2.252 internações de 13 ou 14 dias. Mantivemos todas porque essas durações '
    'estão dentro do intervalo de 1 a 14 dias da base e fazem parte da pergunta. Para emergências '
    'e consultas ambulatoriais prévias, os dois quartis são zero. A regra então sinaliza qualquer '
    'contagem positiva. Os valores foram mantidos como contagens registradas.'
)
