"""Check whether the old all-pairs positional pairing was valid on every dataset."""
import itertools
import numpy as np
from repair_common import *

rows=[]
for name in (MF/'release/mf_field_surrogate_bench/data/roster_25.txt').read_text().splitlines():
    d=ST/'data'/name
    if not list(d.glob('train_l*.npz')):d=next(d.glob('*/train_l1.npz')).parent
    xs={int(p.stem.split('_l')[1]):np.load(p)['x'].astype(np.float32) for p in d.glob('train_l*.npz')}
    bad=[]
    for s,t in itertools.combinations(sorted(xs),2):
        n=min(len(xs[s]),len(xs[t]));m=int(np.sum(np.any(xs[s][:n]!=xs[t][:n],axis=1)))
        if m:bad.append(dict(source=s,target=t,paired_by_position=n,mismatched_inputs=m))
    rows.append(dict(dataset=name,pairs_checked=len(xs)*(len(xs)-1)//2,mismatches=bad))
write_json(ROOT/'PAIRING_AUDIT.json',dict(datasets=rows,affected=[r['dataset'] for r in rows if r['mismatches']]))
print('Positional all-pairs mismatches:',[r['dataset'] for r in rows if r['mismatches']])
