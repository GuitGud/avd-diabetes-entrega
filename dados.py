"""Leitura e preparação da base Diabetes 130-US Hospitals."""
import csv
from decimal import Decimal
import io
import re
from zipfile import ZipFile

import pandas as pd

quantitativas = [
    "time_in_hospital",
    "num_lab_procedures",
    "num_procedures",
    "num_medications",
    "number_outpatient",
    "number_emergency",
    "number_inpatient",
    "number_diagnoses",
]
identificadores = ["encounter_id", "patient_nbr"]
codigos_administrativos = [
    "admission_type_id", "admission_source_id", "discharge_disposition_id"
]
ordem_idade = [f"[{inicio}-{inicio + 10})" for inicio in range(0, 100, 10)]
faixas_libras = [f"[{inicio}-{inicio + 25})" for inicio in range(0, 200, 25)] + [">200"]

campos_nao_informados = ["medical_specialty", "payer_code", "race"]
faixas_comparadas = {"[60-70)": "60 a 69 anos", "[70-80)": "70 a 79 anos"}
rotulos_desfecho = {"NO": "Sem retorno registrado", "<30": "Menos de 30 dias", ">30": "Mais de 30 dias"}

rotulos = {
    "age": "Faixa etária",
    "readmitted": "Desfecho registrado",
    "time_in_hospital": "Permanência (dias)",
    "num_lab_procedures": "Exames laboratoriais",
    "num_procedures": "Procedimentos não laboratoriais",
    "num_medications": "Medicamentos distintos",
    "number_outpatient": "Visitas ambulatoriais no ano anterior",
    "number_emergency": "Emergências no ano anterior",
    "number_inpatient": "Internações no ano anterior",
    "number_diagnoses": "Diagnósticos na internação",

    "weight": "Peso",
    "medical_specialty": "Especialidade médica",
    "payer_code": "Pagador",
    "admission_type_id": "Tipo de admissão",
    "admission_source_id": "Origem da admissão",
    "discharge_disposition_id": "Destino na alta",
    "race": "Raça registrada",
    "diag_1": "Diagnóstico principal",
    "diag_2": "Diagnóstico secundário",
    "diag_3": "Diagnóstico adicional",
    "gender": "Sexo registrado",
    "A1Cresult": "Hemoglobina glicada (HbA1c)",
    "max_glu_serum": "Glicose sérica",
}


def inteiro_pt(valor):
    return f"{valor:,}".replace(",", ".")


def peso_kg(faixa):
    """Converte os limites registrados, sem estimar um peso individual."""
    numeros = re.findall(r"\d+", faixa)
    valores = [Decimal(numero) * Decimal("0.45359237") for numero in numeros]
    formatados = [f"{valor:.2f}".replace(".", ",") for valor in valores]
    if faixa.startswith(">"):
        return f"> {formatados[0]} kg"
    return f"[{formatados[0]} a {formatados[1]}) kg"


conversao_peso = {faixa: peso_kg(faixa) for faixa in faixas_libras}

descricao = {
    "encounter_id": "Código que identifica uma internação no arquivo.",
    "patient_nbr": "Código que reúne as internações do mesmo paciente. Pode aparecer em várias linhas.",
    "race": "Grupo racial registrado na fonte. Contém as categorias branca, afro-americana, asiática, hispânica e outras nas denominações do arquivo. Na cópia de análise, a ausência aparece como Não informado.",
    "gender": "Sexo registrado no atendimento. A fonte usa Female, Male e Unknown/Invalid.",
    "age": "Idade na internação expressa em faixas de dez anos. Em [60–70), 60 pertence ao intervalo e 70 fica na faixa seguinte.",
    "weight": "Faixa de peso registrada na internação. Os limites vieram em libras e foram convertidos para kg. A última categoria fica aberta acima de 200 lb. Não há peso exato por internação.",
    "admission_type_id": "Código do tipo de admissão. Exemplos do dicionário: emergência, urgência, eletiva, recém-nascido e centro de trauma.",
    "discharge_disposition_id": "Código do destino após a internação. Inclui alta para casa, transferência, encaminhamento para cuidados e óbito.",
    "admission_source_id": "Código da origem do encaminhamento para internação. Exemplos: indicação médica, pronto-socorro e transferência de outro serviço.",
    "time_in_hospital": "Dias entre a admissão e a alta. O recorte original inclui internações de 1 a 14 dias.",
    "payer_code": "Código da fonte de pagamento da internação, como operadora, programa de cobertura ou pagamento direto. Na cópia de análise, a ausência aparece como Não informado.",
    "medical_specialty": "Especialidade do profissional responsável pela admissão, como clínica médica, cardiologia ou cirurgia. Na cópia de análise, a ausência aparece como Não informado.",
    "num_lab_procedures": "Total de exames laboratoriais realizados durante a internação.",
    "num_procedures": "Total de procedimentos realizados durante a internação, excluindo os exames laboratoriais.",
    "num_medications": "Quantidade de medicamentos distintos administrados durante a internação, segundo os nomes genéricos registrados.",
    "number_outpatient": "Número de visitas ambulatoriais registradas no ano anterior à internação.",
    "number_emergency": "Número de atendimentos de emergência registrados no ano anterior à internação.",
    "number_inpatient": "Número de internações registradas no ano anterior à internação atual.",
    "diag_1": "Código textual do diagnóstico principal na classificação ICD-9-CM. Pode conter letras, zeros à esquerda ou decimais.",
    "diag_2": "Código textual do diagnóstico secundário em ICD-9-CM. Pode ter preenchimento ausente.",
    "diag_3": "Código textual de outro diagnóstico registrado em ICD-9-CM. Pode ter preenchimento ausente.",
    "number_diagnoses": "Número total de diagnósticos registrados na internação. Pode superar o número de colunas com códigos de diagnóstico.",
    "max_glu_serum": "Faixa de glicose sérica registrada. Norm é a categoria normal, >200 e >300 são categorias de resultado, e None indica exame sem medição.",
    "A1Cresult": "Faixa de hemoglobina glicada registrada. Norm é a categoria normal, >7 e >8 são categorias de resultado, e None indica exame sem medição.",
    "change": "Indica se houve alteração de medicamento ou de dose para diabetes durante a internação. Ch significa que houve alteração e No indica que não houve.",
    "diabetesMed": "Indica se algum medicamento para diabetes foi prescrito. Os valores são Yes e No.",
    "readmitted": "Resultado a comparar na pesquisa. <30 indica retorno registrado em menos de 30 dias, >30 é a categoria de retorno posterior e NO indica que a fonte não registrou retorno.",
}

medicamentos = {
    "metformin": "metformina",
    "repaglinide": "repaglinida",
    "nateglinide": "nateglinida",
    "chlorpropamide": "clorpropamida",
    "glimepiride": "glimepirida",
    "acetohexamide": "acetohexamida",
    "glipizide": "glipizida",
    "glyburide": "glibenclamida",
    "tolbutamide": "tolbutamida",
    "pioglitazone": "pioglitazona",
    "rosiglitazone": "rosiglitazona",
    "acarbose": "acarbose",
    "miglitol": "miglitol",
    "troglitazone": "troglitazona",
    "tolazamide": "tolazamida",
    "examide": "examide, como consta no CSV",
    "citoglipton": "citoglipton, como consta no CSV",
    "insulin": "insulina",
    "glyburide-metformin": "glibenclamida com metformina",
    "glipizide-metformin": "glipizida com metformina",
    "glimepiride-pioglitazone": "glimepirida com pioglitazona",
    "metformin-rosiglitazone": "metformina com rosiglitazona",
    "metformin-pioglitazone": "metformina com pioglitazona",
}

for coluna, nome in medicamentos.items():
    descricao[coluna] = (
        f"Uso de {nome} durante a internação. No indica que não foi prescrito, "
        "Steady indica dose mantida, Up indica aumento e Down indica redução."
    )



def ler_base(fonte):
    """Lê a base original, monta a cópia de análise e abre o dicionário de códigos."""
    entrada = io.BytesIO(fonte) if isinstance(fonte, bytes) else fonte
    with ZipFile(entrada) as arquivo:
        original = pd.read_csv(
            arquivo.open("diabetic_data.csv"),
            keep_default_na=False,
            na_values=["?", "NaN", "nan", ""],
            dtype={"payer_code": str, "diag_1": str, "diag_2": str, "diag_3": str},
            low_memory=False,
        )
        texto_codigos = arquivo.read("IDS_mapping.csv").decode("utf-8-sig")

    mapas = {}
    for linha in csv.reader(io.StringIO(texto_codigos)):
        if not linha:
            continue
        codigo, nome = linha
        if codigo in codigos_administrativos:
            coluna = codigo
            mapas[coluna] = {}
        elif codigo.strip():
            mapas[coluna][int(codigo)] = nome.strip()

    dados = original.loc[~original["gender"].eq("Unknown/Invalid")].copy()
    dados[campos_nao_informados] = dados[campos_nao_informados].fillna("Não informado")
    dados["weight"] = pd.Categorical(
        dados["weight"].map(conversao_peso),
        categories=list(conversao_peso.values()),
        ordered=True,
    )
    return original, dados, mapas


def faixas_de_peso(original):
    return pd.DataFrame({
        "Faixa na fonte (lb)": faixas_libras,
        "Faixa na análise (kg)": list(conversao_peso.values()),
        "Registros da base original": [int(original["weight"].eq(faixa).sum()) for faixa in faixas_libras],
    })


def taxas_reinternacao(dados, *grupos):
    base = dados.dropna(subset=[*grupos, "readmitted"])
    precoce = base["readmitted"].eq("<30")
    chaves = [base[coluna] for coluna in grupos]
    return precoce.groupby(chaves, observed=True).agg(
        internacoes="size", reinternacoes="sum", proporcao="mean"
    )


def percentual_pt(proporcao):
    return f"{proporcao:.2%}".replace(".", ",")


def formatar_taxas(taxas):
    tabela = taxas.rename(columns={
        "internacoes": "Internações",
        "reinternacoes": "Reinternações registradas <30 dias",
        "proporcao": "Proporção",
    }).copy()
    tabela["Proporção"] = tabela["Proporção"].map(percentual_pt)
    return tabela


def catalogar_colunas(original):
    qualitativas = [c for c in original.columns if c not in quantitativas + identificadores]
    assert set(descricao) == set(original.columns)
    tabelas_atributos = {}
    for titulo, colunas in [
        ("Atributos qualitativos", qualitativas),
        ("Atributos quantitativos", quantitativas),
        ("Identificadores", identificadores),
    ]:
        tipos = []
        for coluna in colunas:
            if coluna in ["age", "weight"]:
                tipo = "Ordinal (faixas)"
            elif coluna == "readmitted":
                tipo = "Nominal (alvo)"
            elif coluna == "time_in_hospital":
                tipo = "Duração em dias"
            elif coluna in quantitativas:
                tipo = "Contagem"
            elif coluna in identificadores:
                tipo = "Código"
            else:
                tipo = "Nominal"
            tipos.append(tipo)
        tabela = pd.DataFrame(
            {"Atributo": colunas, "Tipo": tipos, "Descrição": [descricao[c] for c in colunas]}
        )
        tabelas_atributos[titulo] = tabela
    return tabelas_atributos
