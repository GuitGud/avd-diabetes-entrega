"""Figuras estáticas da EDA e do relatório, sem chamadas externas."""
from pathlib import Path
import textwrap
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
# [IA] Claude – imports dos gráficos refeitos
import seaborn as sns
from matplotlib.patches import Patch
from analise import ROOT, NUMERIC, LABELS, AGE_ORDER, ORDER, COLORS, GROUPS, strata_table, rate_by
# [IA] Claude – funções e constantes dos gráficos refeitos
from analise import CORES_BINARIAS, TIPOS_FALTANTE, binary_class, correlations_by_class, kde_counts, ecdf_table

plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.titleweight':'bold','axes.labelcolor':'#263f52','text.color':'#17354b','axes.titlesize':12,'figure.facecolor':'white','savefig.facecolor':'white'})

def save(fig,path):
    fig.tight_layout(pad=1.5)
    fig.savefig(path,dpi=135,bbox_inches='tight')
    plt.close(fig)


def create_figures(raw,df,tables,root=ROOT):
    out=Path(root)/'out/parte_especifica/figuras';out.mkdir(parents=True,exist_ok=True)
    paths={}
    def finish(fig,key):
        p=out/f'{key}.png'; save(fig,p); paths[key]=p
    # [IA] Claude – E1 com duas cores (menos de 30 dias x demais)
    fig,ax=plt.subplots(figsize=(9,4.7))
    tab=pd.crosstab(df.age,binary_class(df)).reindex(index=AGE_ORDER,columns=list(CORES_BINARIAS),fill_value=0)
    bottom=np.zeros(len(tab))
    for c in CORES_BINARIAS:
        ax.bar(np.arange(len(tab)),tab[c],bottom=bottom,label=c,color=CORES_BINARIAS[c]);bottom+=tab[c].to_numpy()
    ax.set(xticks=np.arange(len(tab)),xticklabels=tab.index,title='E1 | Internações por faixa etária',xlabel='Faixa etária (anos)',ylabel='Internações');ax.tick_params(axis='x',rotation=30)
    ax.legend(title='Reinternação',fontsize=8,loc='upper left');finish(fig,'E1')
    fig,ax=plt.subplots(figsize=(9,4.5))
    boxes=ax.boxplot([df.loc[df.desfecho.eq(c),'time_in_hospital'] for c in ORDER],tick_labels=ORDER,patch_artist=True,showfliers=True)
    for patch,c in zip(boxes['boxes'],ORDER):patch.set_facecolor(COLORS[c]);patch.set_alpha(.7)
    ax.set(title='E2 | Permanência por desfecho',xlabel='Categoria de reinternação',ylabel='Permanência (dias)')
    # [IA] Claude – legenda do E2
    ax.legend(handles=[Patch(color=COLORS[c],alpha=.7,label=c) for c in ORDER],title='Reinternação',fontsize=8,loc='upper left',bbox_to_anchor=(1,1));finish(fig,'E2')
    # [IA] Claude – E3 em subplots por desfecho, barras espaçadas e KDE em vermelho
    fig,axes=plt.subplots(1,3,figsize=(15,4.8))
    for ax,c in zip(axes,ORDER):
        v=df.loc[df.desfecho.eq(c),'num_medications'];f=v.value_counts().sort_index()
        ax.bar(f.index,f.values,width=.75,color=COLORS[c],label='Internações')
        curve=kde_counts(v)
        if curve is not None:ax.plot(*curve,color='red',lw=2,label='Densidade (KDE, escala de contagem)')
        ax.set(title=c,xlabel='Medicamentos (contagem)',ylabel='Internações',xlim=(0,85));ax.legend(fontsize=8)
    fig.suptitle('E3 | Medicamentos por internação, por desfecho',fontsize=15);finish(fig,'E3')
    # [IA] Claude – histogramas das 8 variáveis numéricas por categoria do desfecho
    for key,cols in [('H1',NUMERIC[:4]),('H2',NUMERIC[4:])]:
        fig,axes=plt.subplots(len(cols),3,figsize=(14,14),sharex='row')
        for row,c in zip(axes,cols):
            lo,hi=int(raw[c].min()),int(raw[c].max());step=max(1,int(np.ceil((hi-lo+1)/30)))
            bins=np.arange(lo-.5,hi+step+.5,step)
            for ax,o in zip(row,ORDER):
                ax.hist(df.loc[df.desfecho.eq(o),c],bins=bins,rwidth=.9,color=COLORS[o],label=o)
                ax.margins(y=.35);ax.set_title(LABELS[c],fontsize=10);ax.set(xlabel=LABELS[c],ylabel='Contagem de registros');ax.legend(fontsize=8,title='Reinternação',title_fontsize=8)
        fig.suptitle(f'{key} | Histogramas das variáveis numéricas por desfecho',fontsize=15);finish(fig,key)
    # [IA] Claude – E4 com Pearson e Spearman para cada classe do desfecho (4 heatmaps)
    fig,axes=plt.subplots(2,2,figsize=(18,15))
    labels=[textwrap.fill(LABELS[c],17) for c in NUMERIC]
    for ax,((m,k),corr) in zip(axes.flat,correlations_by_class(df).items()):
        sns.heatmap(corr,vmin=-1,vmax=1,cmap='RdBu_r',annot=True,fmt='.2f',annot_kws={'fontsize':12},xticklabels=labels,yticklabels=labels,cbar_kws={'label':f'Coeficiente de {m.title()}'},ax=ax)
        # [IA] Claude – rótulos maiores no E4
        ax.set_title(f'{m.title()} - {k}',fontsize=15);ax.set_xlabel('Variável',fontsize=12);ax.set_ylabel('Variável',fontsize=12)
        ax.figure.axes[-1].tick_params(labelsize=11);ax.figure.axes[-1].yaxis.label.set_size(12)
        ax.tick_params(axis='x',rotation=40,labelsize=11);ax.tick_params(axis='y',rotation=0,labelsize=11);plt.setp(ax.get_xticklabels(),ha='right')
    fig.suptitle('E4 | Matrizes de correlação por classe do desfecho',fontsize=20);finish(fig,'E4')
    ymax=max(rate_by(df,v).percentual.max() for v in ['number_inpatient','number_emergency'])*1.25
    for key,var in [('X1','number_inpatient'),('X2','number_emergency')]:
        t=rate_by(df,var);fig,ax=plt.subplots(figsize=(9,4.5))
        ax.bar(t.grupo,t.percentual,color=['#cf593d' if g=='3 ou mais' else '#93a5b9' for g in t.grupo])
        for i,r in enumerate(t.itertuples()):ax.text(i,r.percentual+.5,f'{r.percentual:.1f}%\nn={r.n:,}',ha='center',fontsize=10)
        ax.set(title=f'{key} | De {t.percentual.iloc[0]:.1f}% a {t.percentual.iloc[-1]:.1f}% por histórico',xlabel=LABELS[var]+' (ano anterior)',ylabel='Reinternações em menos de 30 dias (%)',ylim=(0,ymax))
        # [IA] Claude – legenda com as duas cores usadas nas barras
        ax.legend(handles=[Patch(color='#93a5b9',label='Demais grupos'),Patch(color='#cf593d',label='3 ou mais (destaque)')],title='Reinternação <30 dias',loc='upper left',fontsize=9,title_fontsize=9);finish(fig,key)
    for key,a,b,xlabel,ylabel in [('M1','age','grupo_internacoes','Internações prévias (ano anterior)','Faixa etária (anos)'),('M2','grupo_internacoes','grupo_emergencias','Emergências prévias (ano anterior)','Internações prévias (ano anterior)')]:
        t=strata_table(df,a,b);values=t.pivot(index=a,columns=b,values='percentual');ns=t.pivot(index=a,columns=b,values='n')
        values=values.reindex(index=AGE_ORDER if a=='age' else GROUPS,columns=GROUPS);ns=ns.reindex_like(values)
        fig,ax=plt.subplots(figsize=(9,6 if key=='M1' else 4.5));im=ax.imshow(values.to_numpy(dtype=float),vmin=0,vmax=100,cmap='YlOrRd',aspect='auto')
        for i in range(len(values)):
            for j in range(len(values.columns)):
                if pd.notna(values.iloc[i,j]):ax.text(j,i,f'{values.iloc[i,j]:.1f}%\nn={ns.iloc[i,j]:.0f}',ha='center',va='center',fontsize=8,color='white' if values.iloc[i,j]>55 else '#17354b')
        ax.set(xticks=range(len(values.columns)),xticklabels=values.columns,yticks=range(len(values)),yticklabels=values.index,xlabel=xlabel,ylabel=ylabel,title=f'{key} | Proporção <30 dias em análise multivariada')
        fig.colorbar(im,ax=ax,label='Reinternação <30 dias (%)');finish(fig,key)
    fig,axes=plt.subplots(2,4,figsize=(13,6))
    for ax,c in zip(axes.flat,NUMERIC):
        ax.boxplot(raw[c].dropna(),showfliers=True,flierprops={'markersize':2,'alpha':.2});ax.set_title(textwrap.fill(LABELS[c],22),fontsize=10);ax.set(xlabel='Todas as internações',ylabel='Valor observado',xticks=[])
    # [IA] Claude – legenda e eixo x do Q2
    fig.legend(handles=[plt.Line2D([],[],color='#ff7f0e',label='Mediana'),plt.Line2D([],[],marker='o',ls='',mfc='none',mec='black',label='Extremo (IQR)')],loc='upper right',fontsize=8)
    fig.suptitle('Q2 | Triagem visual de extremos - valores preservados',fontsize=15);finish(fig,'Q2')
    # [IA] Claude – Q1 em contagem, com todos os tipos de faltantes e ordem decrescente
    miss=tables['mecanismos_ausencia'].sort_values('n',ascending=False)
    fig,ax=plt.subplots(figsize=(10,6));ax.barh(miss.atributo,miss.n,color=miss.tipo.map(TIPOS_FALTANTE));ax.invert_yaxis()
    for i,v in enumerate(miss.n):ax.text(v+miss.n.max()*.008,i,f'{v:,}'.replace(',','.'),va='center',fontsize=9)
    ax.set(xlim=(0,miss.n.max()*1.14),xlabel='Contagem de registros',ylabel='Atributo',title='Q1 | Registros faltantes por atributo')
    ax.legend(handles=[Patch(color=v,label=k) for k,v in TIPOS_FALTANTE.items()],title='Tipo de faltante',loc='lower right');finish(fig,'Q1')
    # [IA] Claude – A1 substituído por curvas ECDF das 8 variáveis numéricas
    fig,axes=plt.subplots(2,4,figsize=(15,7))
    for ax,c in zip(axes.flat,NUMERIC):
        t=ecdf_table(raw[c]);ax.step(t.valor,t.acumulada,where='post',color='#27859b',label='ECDF')
        ax.set_title(textwrap.fill(LABELS[c],22),fontsize=10);ax.set(xlabel=LABELS[c],ylabel='Proporção acumulada',ylim=(0,1.03));ax.legend(fontsize=8,loc='lower right')
    fig.suptitle('A1 | Distribuição acumulada (ECDF) das variáveis numéricas',fontsize=15);finish(fig,'A1')
    # [IA] Claude – A2 com barras verticais
    categories=[c for c in raw if c not in NUMERIC+['encounter_id','patient_nbr']]
    for page,start in enumerate(range(0,len(categories),8),1):
        fig,axes=plt.subplots(4,2,figsize=(14,19))
        for ax,c in zip(axes.flat,categories[start:start+8]):
            s=raw[c].fillna('Não informado').value_counts();top=s.head(7).copy()
            if len(s)>7:top.loc['Outras (agregado)']=s.iloc[7:].sum()
            top=top.sort_values(ascending=False);x=np.arange(len(top))
            ax.bar(x,top.values,width=.75,color='#27859b',label='Internações')
            # [IA] Claude – rótulos maiores no A2
            ax.set_title(c,fontsize=15);ax.set_xlabel('Categoria',fontsize=12);ax.set_ylabel('Internações',fontsize=12);ax.set_xticks(x)
            ax.set_xticklabels([str(v)[:26] for v in top.index],rotation=35,ha='right',fontsize=11);ax.tick_params(axis='y',labelsize=11);ax.legend(fontsize=11,loc='upper right')
        for ax in axes.flat[len(categories[start:start+8]):]:ax.axis('off')
        fig.suptitle(f'A2.{page} | Distribuições categóricas - página {page}',fontsize=20);finish(fig,f'A2_{page}')
    # [IA] Claude – C1: taxa <30 dias por histórico, base com NO × somente reinternados (sem NO)
    bases={'Todas as internações (com NO)':df,'Somente reinternados (sem NO)':df.loc[df.readmitted.ne('NO')]}
    cores={'Todas as internações (com NO)':'#94a3b8','Somente reinternados (sem NO)':'#2a7f96'}
    variaveis={'number_inpatient':'Internações prévias (ano anterior)','number_emergency':'Emergências prévias (ano anterior)'}
    taxas={(b,v):rate_by(g,v).set_index('grupo').reindex(GROUPS) for b,g in bases.items() for v in variaveis}
    ymax=max(t.percentual.max() for t in taxas.values())*1.25
    fig,axes=plt.subplots(1,2,figsize=(14.5,5.8),sharey=True);largura=.38
    for ax,(v,rotulo) in zip(axes,variaveis.items()):
        for k,(b,cor) in enumerate(cores.items()):
            t=taxas[(b,v)];x=np.arange(len(GROUPS))+(k-.5)*largura
            ax.bar(x,t.percentual,width=largura,color=cor,label=b)
            for xi,pc,n in zip(x,t.percentual,t.n):
                if pd.notna(pc):ax.text(xi,pc+.6,f'{pc:.1f}%\nn={int(n):,}'.replace(',','.'),ha='center',va='bottom',fontsize=7.5)
        ax.set_xticks(range(len(GROUPS)),GROUPS);ax.set_title(rotulo,fontsize=11);ax.set_xlabel(rotulo);ax.set_ylim(0,ymax)
    axes[0].set_ylabel('Reinternações em menos de 30 dias (%)');axes[0].legend(title='Base analisada',loc='upper left',fontsize=9)
    fig.suptitle('C1 | Taxa de reinternação em menos de 30 dias por histórico: base com e sem as linhas NO',fontsize=12,fontweight='bold');finish(fig,'C1')
    return paths
