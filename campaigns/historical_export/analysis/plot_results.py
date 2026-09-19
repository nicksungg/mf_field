"""Standalone scientific summary, separate from the frozen training sources."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT=Path(__file__).resolve().parents[1]
METHODS={'field_gate_shared':'Shared field gate','field_gate_specific':'Model-specific field gate',
         'field_rules':'Readable rules','constant_features_specific':'Gate with constant field features',
         'expert:mf_fno_allpairs':'All-pairs single model',
         'oracle_case_mixture':'Best possible per-case mixture'}
COLORS=['#246b8e','#b15b36','#64853a','#c89d34','#7b4d97','#929292']

def main():
    df=pd.read_csv(ROOT/'results/results.csv')
    fig,axes=plt.subplots(1,2,figsize=(13,6))
    for ax,protocol,title in zip(axes,['cases','class'],['New cases in known classes','Class withheld from gate training']):
        part=df[df.protocol==protocol]
        mean=part.groupby(['dataset','class_name','method']).error.mean().unstack('method')
        ratios=mean[list(METHODS)].div(mean['calibration_fixed'],axis=0)
        means=np.exp(np.log(ratios).groupby(level='class_name').mean()).sort_index()
        ypos=np.arange(len(means));offsets=np.linspace(-.24,.24,len(METHODS))
        for (method,label),color,off in zip(METHODS.items(),COLORS,offsets):
            ax.scatter(means[method],ypos+off,s=43,color=color,label=label,zorder=3)
        ax.axvline(1,color='#343434',linestyle='--',linewidth=1)
        ax.set_xscale('log');ax.set_yticks(ypos,means.index.str.replace('_',' '));ax.invert_yaxis()
        ax.set_xlabel('Error / fixed mixture using all calibration labels\nBelow 1 is better')
        ax.set_title(title,loc='left',fontweight='bold');ax.grid(axis='x',alpha=.18)
        for spine in ['top','right']:ax.spines[spine].set_visible(False)
    handles,labels=axes[1].get_legend_handles_labels()
    fig.legend(handles,labels,loc='lower center',bbox_to_anchor=(.5,.015),
               ncol=3,fontsize=9,frameon=False)
    fig.suptitle('Do predicted-field features improve averaging?',fontsize=15,fontweight='bold')
    fig.subplots_adjust(left=.12,right=.985,top=.87,bottom=.25,wspace=.38)
    fig.savefig(ROOT/'results/fieldgate_comparison.png',dpi=180)
    fig.savefig(ROOT/'results/fieldgate_comparison.pdf')

    summary={}
    for protocol in ['cases','class','class_lf_seen_diagnostic']:
        part=df[df.protocol==protocol]
        if part.empty:continue
        mean=part.groupby(['dataset','class_name','method']).error.mean().unstack('method')
        ratios=mean.div(mean['calibration_fixed'],axis=0)
        aggregate=np.exp(np.log(ratios.clip(lower=1e-15)).groupby(level='class_name').mean().mean())
        summary[protocol]={m:dict(class_balanced_error_ratio=float(aggregate[m]),
             wins=int((ratios[m]<1-1e-6).sum()),datasets=len(ratios)) for m in ratios.columns}
    (ROOT/'results/summary.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))

if __name__=='__main__':main()
