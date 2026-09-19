"""Standalone visualization; not imported by fitting jobs."""
from pathlib import Path
import json
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
r=Path(__file__).resolve().parents[1]
s=json.loads((r/'results/summary.json').read_text())
methods=['gate_current','gate_input','gate_local','gate_input_local']
labels=['Current field summaries','+ simulation inputs','+ local field summaries','+ inputs and local summaries']
fig,axes=plt.subplots(1,2,figsize=(12,5))
y=np.arange(4)
for pool,color,offset in [('seven','#326d93',-.13),('nine','#c47739',.13)]:
    q=s['pools'][pool]['comparisons']['calibration_fixed']
    values=[q[m]['class_balanced_ratio'] for m in methods]
    axes[0].scatter(values,y+offset,label=f'{pool.capitalize()} experts',color=color,s=55)
axes[0].set_yticks(y,labels);axes[0].invert_yaxis();axes[0].axvline(1,linestyle='--',color='.4')
axes[0].set_xlabel('Error / fixed mixture using fit + tuning labels\nSame expert pool; below 1 is better')
axes[0].set_title('Do the extra features help?',loc='left',fontweight='bold')
axes[0].legend(frameon=False,loc='best')
q=s['nine_vs_seven']['calibration_fixed']['class_ratios']
classes=sorted(q);values=[q[c] for c in classes]
axes[1].scatter(values,np.arange(len(classes)),s=55,color='#527c4c')
axes[1].set_yticks(np.arange(len(classes)),[c.replace('_',' ') for c in classes]);axes[1].invert_yaxis()
axes[1].axvline(1,linestyle='--',color='.4');axes[1].set_xscale('log')
axes[1].set_xlabel('Nine-expert / seven-expert fixed-mixture error\nBelow 1 is better')
axes[1].set_title('Do the two correctors help?',loc='left',fontweight='bold')
for ax in axes:
    ax.grid(axis='x',alpha=.2)
    for spine in ['top','right']:ax.spines[spine].set_visible(False)
fig.suptitle('Input parameters, local summaries and additional experts',fontweight='bold')
fig.subplots_adjust(left=.22,right=.98,bottom=.2,top=.85,wspace=.65)
fig.savefig(r/'results/comparison.png',dpi=180)
fig.savefig(r/'results/comparison.pdf')
