"""Verificações de preenchimento e domínio feitas no CSV original."""
import pandas as pd

from dados import ordem_idade, faixas_libras, medicamentos, quantitativas


def auditar(original, mapas):
    faltantes = original.isna().sum()
    sem_informacao = {"null", "not available", "not mapped", "unknown/invalid"}
    problemas = []
    mascaras = {}
    genero_invalido = original["gender"].eq("Unknown/Invalid")


    def registrar(atributo, motivo, mascara):
        contagem = int(mascara.sum())
        if contagem:
            problemas.append((atributo, motivo, contagem))
            anterior = mascaras.get(atributo, pd.Series(False, index=original.index))
            mascaras[atributo] = anterior | mascara


    for coluna in faltantes[faltantes.gt(0)].index:
        registrar(coluna, "Valor ausente", original[coluna].isna())

    for coluna, mapa in mapas.items():
        codigos_sem_dado = [codigo for codigo, nome in mapa.items() if nome.lower() in sem_informacao]
        registrar(coluna, "Código sem informação", original[coluna].isin(codigos_sem_dado))
        codigo_nao_listado = original[coluna].notna() & ~original[coluna].isin(mapa)
        registrar(coluna, "Código fora do dicionário", codigo_nao_listado)

    registrar("gender", "Categoria desconhecida ou inválida", genero_invalido)
    registrar("encounter_id", "ID de internação duplicado", original["encounter_id"].duplicated())

    dominios = {
        "age": ordem_idade,
        "weight": faixas_libras,
        "gender": ["Female", "Male", "Unknown/Invalid"],
        "race": ["Caucasian", "AfricanAmerican", "Asian", "Hispanic", "Other"],
        "readmitted": ["NO", ">30", "<30"],
        "change": ["No", "Ch"],
        "diabetesMed": ["No", "Yes"],
        "A1Cresult": ["None", "Norm", ">7", ">8"],
        "max_glu_serum": ["None", "Norm", ">200", ">300"],
    }
    dominios.update({coluna: ["No", "Steady", "Up", "Down"] for coluna in medicamentos})
    for coluna, categorias in dominios.items():
        fora = original[coluna].notna() & ~original[coluna].isin(categorias)
        registrar(coluna, "Categoria fora do domínio", fora)

    for coluna in quantitativas:
        numerica = pd.to_numeric(original[coluna], errors="coerce")
        minimo = 1 if coluna in ["time_in_hospital", "num_lab_procedures", "num_medications"] else 0
        fora = numerica.isna() | numerica.mod(1).ne(0) | numerica.lt(minimo)
        if coluna == "time_in_hospital":
            fora |= numerica.gt(14)
        registrar(coluna, "Contagem ou duração fora do domínio", original[coluna].notna() & fora)

    for coluna in ["diag_1", "diag_2", "diag_3"]:
        # A fonte tem códigos numéricos abreviados. Só verificamos o formato geral.
        formato_valido = original[coluna].str.fullmatch(r"(?:\d{1,3}|[EV]\d{2,3})(?:\.\d{1,2})?", na=True)
        registrar(coluna, "Formato de código fora do padrão verificado", ~formato_valido)

    qualidade = pd.DataFrame(problemas, columns=["Atributo", "Problema", "Registros"])
    qualidade = qualidade.sort_values("Registros", ascending=False, ignore_index=True)
    qualidade["Percentual"] = qualidade["Registros"].map(
        lambda n: f"{100 * n / len(original):.2f}%".replace(".", ",")
    )
    exames = pd.Series({
        "A1Cresult": int(original["A1Cresult"].eq("None").sum()),
        "max_glu_serum": int(original["max_glu_serum"].eq("None").sum()),
    }, name="Exames sem medição")
    contagens = pd.Series(
        {coluna: int(mascara.sum()) for coluna, mascara in mascaras.items()},
        name="Registros com problema",
    )
    return qualidade, contagens, exames
