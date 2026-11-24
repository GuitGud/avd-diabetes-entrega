"""As seis figuras da análise, usadas também pelo painel."""
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter, PercentFormatter

from dados import faixas_comparadas, inteiro_pt, percentual_pt, rotulos, rotulos_desfecho

AZUL = '#315f89'
VERDE = '#54776a'
LARANJA = '#a84e36'


def grafico_qualidade(contagens, exames):
    fig, paineis = plt.subplots(1, 2, figsize=(13.5, 4.8), layout='constrained')
    limite = max(contagens.max(), exames.max()) * 1.18
    for ax, valores, cor, titulo in [
        (paineis[0], contagens, AZUL, 'Campos com informação ausente ou inválida'),
        (paineis[1], exames, VERDE, 'Exames registrados como não medidos'),
    ]:
        valores = valores.sort_values()
        nomes = [rotulos.get(coluna, coluna) for coluna in valores.index]
        barras = ax.barh(nomes, valores, color=cor)
        ax.bar_label(barras, labels=[inteiro_pt(n) for n in valores], padding=4, fontsize=9)
        ax.set(title=titulo, xlabel='Internações (contagem)', xlim=(0, limite))
        ax.xaxis.set_major_formatter(FuncFormatter(lambda n, _: inteiro_pt(int(n))))
        ax.grid(axis='x', alpha=0.2)
        ax.set_axisbelow(True)
    fig.suptitle('Q1. Preenchimento da base original', fontweight='bold')
    return fig


def grafico_peso(faixas, ausentes):
    totais = faixas['Registros da base original']
    fig, ax = plt.subplots(figsize=(9, 4.5), layout='constrained')
    barras = ax.barh(faixas['Faixa na análise (kg)'], totais, color=AZUL,
                     label='Internações com peso registrado')
    ax.bar_label(barras, labels=[inteiro_pt(n) for n in totais], padding=5)
    ax.set(
        title=f'Faixas de peso registradas\n{inteiro_pt(totais.sum())} preenchidas e {inteiro_pt(ausentes)} ausentes',
        xlabel='Internações', ylabel='Faixa de peso (kg)', xlim=(0, totais.max() * 1.15),
    )
    ax.invert_yaxis()
    ax.xaxis.set_major_formatter(FuncFormatter(lambda n, _: inteiro_pt(int(n))))
    ax.legend(loc='lower right')
    return fig


def grafico_duracoes(frequencia):
    fig, ax = plt.subplots(figsize=(10, 4), layout='constrained')
    maior = frequencia.idxmax()
    cores = [AZUL if dia == maior else '#9cb6ca' for dia in frequencia.index]
    ax.bar(frequencia.index, frequencia.values, color=cores, label='Internações')
    ax.annotate(inteiro_pt(frequencia.loc[maior]), (maior, frequencia.loc[maior]),
                xytext=(0, 5), textcoords='offset points', ha='center')
    ax.set(title='Internações por duração', xlabel='Permanência (dias)',
           ylabel='Internações', xticks=range(1, 15), ylim=(0, frequencia.max() * 1.17))
    ax.yaxis.set_major_formatter(FuncFormatter(lambda n, _: inteiro_pt(int(n))))
    ax.legend()
    return fig


def grafico_caixas(duracoes_por_desfecho):
    fig, ax = plt.subplots(figsize=(9, 4.3), layout='constrained')
    caixas = ax.boxplot(
        list(duracoes_por_desfecho.values()),
        patch_artist=True,
        boxprops={'facecolor': '#dce8f0', 'edgecolor': AZUL},
        medianprops={'color': LARANJA, 'linewidth': 2},
        flierprops={'marker': 'o', 'markersize': 3, 'alpha': 0.3, 'markeredgecolor': AZUL},
    )
    ax.set_xticks(range(1, len(duracoes_por_desfecho) + 1),
                  [rotulos_desfecho[codigo] for codigo in duracoes_por_desfecho])
    ax.set(title='Permanência conforme o desfecho registrado', xlabel='Desfecho',
           ylabel='Permanência (dias)', ylim=(0.2, 15), yticks=range(2, 15, 2))
    ax.legend(handles=[caixas['boxes'][0], caixas['medians'][0]],
              labels=['50% centrais (Q1 a Q3)', 'Mediana'], loc='upper left')
    return fig


def grafico_taxa_dia(taxas):
    fig, ax = plt.subplots(figsize=(12, 4.3), layout='constrained')
    ax.scatter(taxas.index, taxas['proporcao'], color=AZUL, s=42,
               label='Proporção em cada duração')
    for dia, proporcao in taxas['proporcao'].items():
        ax.annotate(percentual_pt(proporcao), (dia, proporcao), xytext=(0, 8),
                    textcoords='offset points', ha='center', fontsize=9)
    totais = taxas['internacoes'].to_dict()
    rotulos_dias = [f'{dia}\nn={inteiro_pt(totais[dia])}' if dia in totais else str(dia)
                    for dia in range(1, 15)]
    ax.set_xticks(range(1, 15), rotulos_dias, fontsize=8)
    ax.set(title='Reinternação registrada em menos de 30 dias',
           xlabel='Permanência (dias) e total do grupo (n)', ylabel='Proporção de internações',
           xlim=(0.4, 14.6), ylim=(0, min(1.1, max(0.18, taxas['proporcao'].max() * 1.22))))
    ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    ax.grid(axis='y', alpha=0.2)
    ax.set_axisbelow(True)
    ax.legend(loc='lower left')
    return fig


def grafico_taxa_idade(taxas):
    fig, ax = plt.subplots(figsize=(10.5, 4.2), layout='constrained')
    for (faixa, nome), cor, marcador, deslocamento in zip(
        faixas_comparadas.items(), [AZUL, LARANJA], ['o', 's'], [-0.13, 0.13],
    ):
        if faixa not in taxas.index.get_level_values('age'):
            continue
        serie = taxas.xs(faixa, level='age')['proporcao']
        ax.scatter(serie.index + deslocamento, serie, color=cor, marker=marcador,
                   label=nome, s=42)
    ax.set(title='Reinternação em menos de 30 dias nas duas faixas etárias mais frequentes',
           xlabel='Permanência (dias)', ylabel='Proporção de internações',
           xlim=(0.4, 14.6), ylim=(0, min(1.05, max(0.20, taxas['proporcao'].max() * 1.2))),
           xticks=range(1, 15))
    ax.yaxis.set_major_formatter(PercentFormatter(1, decimals=0))
    ax.grid(axis='y', alpha=0.2)
    ax.set_axisbelow(True)
    ax.legend(loc='lower left', ncols=2)
    return fig
