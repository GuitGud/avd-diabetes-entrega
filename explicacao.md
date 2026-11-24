# Como lemos a base de internações

Como a proporção de reinternações registradas em menos de 30 dias varia conforme a duração da internação?

**Público** · Turma e professora de Análise e Visualização de Dados.

As proporções de reinternação registrada diferem entre as durações e oscilam de um dia para o outro. Entre internações de dez, 11 e 12 dias, foram 14,35%, 10,51% e 13,33%. O recorte por idade permite ver também como essas proporções variam entre as duas faixas mais frequentes para a mesma duração.

## Como seguir a análise

Abra o Colab e siga pela ordem das células. A base original alimenta a auditoria e os gráficos de preenchimento e peso. A cópia de análise alimenta os totais, as medidas, os boxplots e as proporções.

## Onde estão os critérios da Parte Específica

| Critério | Onde conferir |
|---|---|
| Estrutura e tipos | Colab e apêndice do relatório com os 50 atributos. |
| Qualidade e tratamento | Tabelas de nulos, duplicatas, códigos e Q1. |
| Estatísticas e extremos | Resumo de medidas, exemplo de emergências e triagem pelo IQR. |
| História e pergunta | Quatro figuras de exploração levam à proporção por duração e à comparação por idade. |
| Notas de leitura | Calcule, leia os números e veja o motivo de cada escolha junto à figura. |
| Dashboard Streamlit | Última célula do notebook e código em `src/parte_especifica/dashboard.py`. |

## Leitura, conversão e qualidade

`ler_base` abre o ZIP e lê `diabetic_data.csv` e `IDS_mapping.csv`. A auditoria usa `isna().sum()` para nulos e `duplicated().sum()` para duplicatas. `auditar` confere o domínio dos números e categorias e os códigos administrativos. Os dois limites de cada faixa de peso são multiplicados por 0,45359237.

**Sexo registrado** · A categoria desconhecida ou inválida aparece em três registros, todos sem retorno registrado. Retiramos essas linhas da cópia de análise. Passamos de 101.766 para 101.763 internações e mantivemos os mesmos 11.357 casos registrados em menos de 30 dias. O arquivo não identifica a causa da categoria inválida.

**Especialidade, pagador e raça** · Mantivemos as internações e marcamos os campos vazios como Não informado. Isso permite contar quem ficou sem informação. O arquivo mostra os campos incompletos, mas não traz o processo de coleta para identificar a causa de cada ausência.

**Diagnósticos** · Os códigos ausentes continuam nulos. Das 358 internações sem segundo diagnóstico, 219 tinham total menor que dois. Das 1.423 sem terceiro diagnóstico, 1.242 tinham total menor que três. A contagem ajuda a entender por que algumas posições podem estar vazias. Nos demais casos e entre os 21 sem primeiro diagnóstico, não há informação suficiente para recuperar o código.

**Peso** · A base original tem 3.197 faixas preenchidas. Convertemos os limites de libras para kg e mantivemos em branco os pesos ausentes. Permanência e desfecho estão preenchidos também nessas linhas, por isso elas continuam na pesquisa principal.

**Admissão e alta** · Alguns códigos significam que o campo está indisponível, desconhecido ou sem mapeamento. Conferimos o dicionário e os contamos na auditoria. Os códigos originais permanecem na cópia de análise.

**Exames** · O valor None em HbA1c e glicose sérica indica que o exame não foi medido. Ele fica separado das ausências e dos resultados medidos.

## Distribuições e extremos

Em emergências prévias, 90.380 internações tinham zero atendimento registrado no ano anterior. O percentil 99 foi 3 e o máximo foi 76. A assimetria de 22,86 indica uma cauda longa à direita. A curtose de Fisher de 1.191,65 mostra quanto os valores extremos pesam nessa medida. A média fica em 0,20. Junto com o percentil e o máximo, ela ajuda a ver o contraste entre o volume de registros com poucas emergências e o tamanho dos valores mais altos.

Para cada medida, calculamos o primeiro e o terceiro quartil e a distância entre eles (IQR). Sinalizamos valores abaixo de Q1 − 1,5 × IQR ou acima de Q3 + 1,5 × IQR. Na permanência, a regra marcou 2.252 internações de 13 ou 14 dias. Mantivemos todas porque essas durações estão dentro do intervalo de 1 a 14 dias da base e fazem parte da pergunta. Para emergências e consultas ambulatoriais prévias, os dois quartis são zero. A regra então sinaliza qualquer contagem positiva. Os valores foram mantidos como contagens registradas.

## Como foram calculadas as proporções

`taxas_reinternacao` agrupa as linhas pela duração e, no segundo gráfico, também pela idade. Em cada grupo, `size` conta as internações e `sum` soma os registros cujo desfecho é `<30`. A média do indicador booleano é a divisão desses dois totais.

## O que mostramos e por quê

### Q1. Preenchimento da base

Quantas internações têm informação ausente ou inválida em cada coluna da base original. O painel ao lado conta exames que ficaram registrados como não medidos.

Peso foi a coluna menos preenchida, com 98.569 ausências. Especialidade veio em seguida, com 49.949. Uma comparação que usa peso parte de 3.197 internações com a informação disponível.

As barras ordenadas criam uma hierarquia e destacam as colunas com mais ocorrências. Os painéis usam a mesma escala e distinguem ausências de exames não medidos.

### Faixas de peso em kg

Contagem de internações nas faixas de peso preenchidas na base original. Os limites aparecem em kg.

Entre os 3.197 registros com faixa de peso, a faixa de aproximadamente 34,02 a 45,36 kg foi a mais frequente, com 1.336 registros.

Cada faixa é uma categoria. As barras permitem comparar quantos registros há em cada faixa e deixam os rótulos legíveis.

### Internações por duração

Total de internações para cada duração, de 1 a 14 dias.

Três dias foi a duração mais frequente, com 17.756 internações.

As barras comparam contagens em dias inteiros. A barra mais escura e o rótulo acima dela localizam a duração mais frequente.

### Permanência por desfecho

Distribuição da duração da internação para cada categoria de reinternação registrada.

A mediana foi de três dias no grupo sem retorno registrado e de quatro dias nos dois grupos com retorno. Os 50% centrais ficam entre dois e seis dias nos três grupos.

O boxplot mostra a mediana e a faixa entre o primeiro e o terceiro quartil na mesma escala. A linha em cor de destaque indica a mediana.

### Reinternação por dia de permanência

Em cada duração, divide os casos registrados em menos de 30 dias pelo total de internações do grupo. O eixo horizontal traz o total usado em cada cálculo.

A proporção foi de 14,35% entre as internações de dez dias, 10,51% entre as de 11 dias e 13,33% entre as de 12 dias. As proporções oscilam de um dia de permanência para o outro.

Um ponto por dia mantém visíveis as oscilações. A altura mostra a proporção, as porcentagens aparecem sobre os pontos e os totais ficam abaixo dos dias.

### Permanência e reinternação por faixa etária

Proporções por duração nas duas faixas etárias mais frequentes na cópia de análise. A tabela mostra os casos e os totais de cada faixa e duração.

Entre as internações de dez dias, foram 76 casos em 554 internações de pessoas de 60 a 69 anos (13,72%) e 103 em 645 de pessoas de 70 a 79 anos (15,97%).

Dois símbolos e cores na mesma escala distinguem as faixas. Os pontos lado a lado permitem comparar as duas proporções para a mesma duração.

## Dicionário dos 50 atributos

As três tabelas abaixo estão também no Colab. O painel permite consultar a descrição de cada coluna.

### Atributos qualitativos

| Atributo | Tipo | Descrição |
|---|---|---|
| race | Nominal | Grupo racial registrado na fonte. Contém as categorias branca, afro-americana, asiática, hispânica e outras nas denominações do arquivo. Na cópia de análise, a ausência aparece como Não informado. |
| gender | Nominal | Sexo registrado no atendimento. A fonte usa Female, Male e Unknown/Invalid. |
| age | Ordinal (faixas) | Idade na internação expressa em faixas de dez anos. Em [60–70), 60 pertence ao intervalo e 70 fica na faixa seguinte. |
| weight | Ordinal (faixas) | Faixa de peso registrada na internação. Os limites vieram em libras e foram convertidos para kg. A última categoria fica aberta acima de 200 lb. Não há peso exato por internação. |
| admission_type_id | Nominal | Código do tipo de admissão. Exemplos do dicionário: emergência, urgência, eletiva, recém-nascido e centro de trauma. |
| discharge_disposition_id | Nominal | Código do destino após a internação. Inclui alta para casa, transferência, encaminhamento para cuidados e óbito. |
| admission_source_id | Nominal | Código da origem do encaminhamento para internação. Exemplos: indicação médica, pronto-socorro e transferência de outro serviço. |
| payer_code | Nominal | Código da fonte de pagamento da internação, como operadora, programa de cobertura ou pagamento direto. Na cópia de análise, a ausência aparece como Não informado. |
| medical_specialty | Nominal | Especialidade do profissional responsável pela admissão, como clínica médica, cardiologia ou cirurgia. Na cópia de análise, a ausência aparece como Não informado. |
| diag_1 | Nominal | Código textual do diagnóstico principal na classificação ICD-9-CM. Pode conter letras, zeros à esquerda ou decimais. |
| diag_2 | Nominal | Código textual do diagnóstico secundário em ICD-9-CM. Pode ter preenchimento ausente. |
| diag_3 | Nominal | Código textual de outro diagnóstico registrado em ICD-9-CM. Pode ter preenchimento ausente. |
| max_glu_serum | Nominal | Faixa de glicose sérica registrada. Norm é a categoria normal, >200 e >300 são categorias de resultado, e None indica exame sem medição. |
| A1Cresult | Nominal | Faixa de hemoglobina glicada registrada. Norm é a categoria normal, >7 e >8 são categorias de resultado, e None indica exame sem medição. |
| metformin | Nominal | Uso de metformina durante a internação. No indica que não foi prescrito, Steady indica dose mantida, Up indica aumento e Down indica redução. |
| repaglinide | Nominal | Uso de repaglinida durante a internação. No indica que não foi prescrito, Steady indica dose mantida, Up indica aumento e Down indica redução. |
| nateglinide | Nominal | Uso de nateglinida durante a internação. No indica que não foi prescrito, Steady indica dose mantida, Up indica aumento e Down indica redução. |
| chlorpropamide | Nominal | Uso de clorpropamida durante a internação. No indica que não foi prescrito, Steady indica dose mantida, Up indica aumento e Down indica redução. |
| glimepiride | Nominal | Uso de glimepirida durante a internação. No indica que não foi prescrito, Steady indica dose mantida, Up indica aumento e Down indica redução. |
| acetohexamide | Nominal | Uso de acetohexamida durante a internação. No indica que não foi prescrito, Steady indica dose mantida, Up indica aumento e Down indica redução. |
| glipizide | Nominal | Uso de glipizida durante a internação. No indica que não foi prescrito, Steady indica dose mantida, Up indica aumento e Down indica redução. |
| glyburide | Nominal | Uso de glibenclamida durante a internação. No indica que não foi prescrito, Steady indica dose mantida, Up indica aumento e Down indica redução. |
| tolbutamide | Nominal | Uso de tolbutamida durante a internação. No indica que não foi prescrito, Steady indica dose mantida, Up indica aumento e Down indica redução. |
| pioglitazone | Nominal | Uso de pioglitazona durante a internação. No indica que não foi prescrito, Steady indica dose mantida, Up indica aumento e Down indica redução. |
| rosiglitazone | Nominal | Uso de rosiglitazona durante a internação. No indica que não foi prescrito, Steady indica dose mantida, Up indica aumento e Down indica redução. |
| acarbose | Nominal | Uso de acarbose durante a internação. No indica que não foi prescrito, Steady indica dose mantida, Up indica aumento e Down indica redução. |
| miglitol | Nominal | Uso de miglitol durante a internação. No indica que não foi prescrito, Steady indica dose mantida, Up indica aumento e Down indica redução. |
| troglitazone | Nominal | Uso de troglitazona durante a internação. No indica que não foi prescrito, Steady indica dose mantida, Up indica aumento e Down indica redução. |
| tolazamide | Nominal | Uso de tolazamida durante a internação. No indica que não foi prescrito, Steady indica dose mantida, Up indica aumento e Down indica redução. |
| examide | Nominal | Uso de examide, como consta no CSV durante a internação. No indica que não foi prescrito, Steady indica dose mantida, Up indica aumento e Down indica redução. |
| citoglipton | Nominal | Uso de citoglipton, como consta no CSV durante a internação. No indica que não foi prescrito, Steady indica dose mantida, Up indica aumento e Down indica redução. |
| insulin | Nominal | Uso de insulina durante a internação. No indica que não foi prescrito, Steady indica dose mantida, Up indica aumento e Down indica redução. |
| glyburide-metformin | Nominal | Uso de glibenclamida com metformina durante a internação. No indica que não foi prescrito, Steady indica dose mantida, Up indica aumento e Down indica redução. |
| glipizide-metformin | Nominal | Uso de glipizida com metformina durante a internação. No indica que não foi prescrito, Steady indica dose mantida, Up indica aumento e Down indica redução. |
| glimepiride-pioglitazone | Nominal | Uso de glimepirida com pioglitazona durante a internação. No indica que não foi prescrito, Steady indica dose mantida, Up indica aumento e Down indica redução. |
| metformin-rosiglitazone | Nominal | Uso de metformina com rosiglitazona durante a internação. No indica que não foi prescrito, Steady indica dose mantida, Up indica aumento e Down indica redução. |
| metformin-pioglitazone | Nominal | Uso de metformina com pioglitazona durante a internação. No indica que não foi prescrito, Steady indica dose mantida, Up indica aumento e Down indica redução. |
| change | Nominal | Indica se houve alteração de medicamento ou de dose para diabetes durante a internação. Ch significa que houve alteração e No indica que não houve. |
| diabetesMed | Nominal | Indica se algum medicamento para diabetes foi prescrito. Os valores são Yes e No. |
| readmitted | Nominal (alvo) | Resultado a comparar na pesquisa. <30 indica retorno registrado em menos de 30 dias, >30 é a categoria de retorno posterior e NO indica que a fonte não registrou retorno. |

### Atributos quantitativos

| Atributo | Tipo | Descrição |
|---|---|---|
| time_in_hospital | Duração em dias | Dias entre a admissão e a alta. O recorte original inclui internações de 1 a 14 dias. |
| num_lab_procedures | Contagem | Total de exames laboratoriais realizados durante a internação. |
| num_procedures | Contagem | Total de procedimentos realizados durante a internação, excluindo os exames laboratoriais. |
| num_medications | Contagem | Quantidade de medicamentos distintos administrados durante a internação, segundo os nomes genéricos registrados. |
| number_outpatient | Contagem | Número de visitas ambulatoriais registradas no ano anterior à internação. |
| number_emergency | Contagem | Número de atendimentos de emergência registrados no ano anterior à internação. |
| number_inpatient | Contagem | Número de internações registradas no ano anterior à internação atual. |
| number_diagnoses | Contagem | Número total de diagnósticos registrados na internação. Pode superar o número de colunas com códigos de diagnóstico. |

### Identificadores

| Atributo | Tipo | Descrição |
|---|---|---|
| encounter_id | Código | Código que identifica uma internação no arquivo. |
| patient_nbr | Código | Código que reúne as internações do mesmo paciente. Pode aparecer em várias linhas. |

## Arquivos e execução

- `Dashboard_Diabetes_Colab.ipynb` contém dados, células da exploração e inicialização do painel.
- `src/parte_especifica/dados.py` carrega a base, faz a conversão, guarda o dicionário e agrupa as proporções.
- `qualidade.py` e `graficos.py` contêm as verificações e as figuras usadas no notebook e no painel.
- `textos.py` guarda as notas de leitura e as decisões adotadas.
- `out/parte_especifica/` reúne as figuras e as tabelas calculadas.
- O relatório traz a análise documentada. O guia reúne as falas para a defesa.

A análise compara internações, e uma pessoa pode contribuir com várias linhas. O desfecho é o que ficou registrado no conjunto de dados. As proporções descrevem grupos observados e não permitem atribuir a variação à duração da internação ou à faixa etária.

**Referências** · [UCI](https://archive.ics.uci.edu/dataset/296/diabetes-130-us-hospitals-for-years-1999-2008), [artigo de origem](https://doi.org/10.1155/2014/781670), [conversão de unidades](https://nvlpubs.nist.gov/nistpubs/hb/2026/NIST.HB.44-2026.pdf) e [pandas](https://pandas.pydata.org/docs/reference/api/pandas.DataFrame.kurt.html).
