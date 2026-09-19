"""Separate HF-label overlap from LF-input overlap, without loading test answers."""
import json
import re
import numpy as np
from config import *

def main():
    plan=json.loads((ROOT/'plan.json').read_text())
    for d in plan['datasets']:
        exports=[np.load(ROOT/'predictions'/f'{m}__{d}.npz') for m in MODELS]
        theta=exports[0]['theta'];overlap=np.logical_or.reduce([z['base_train_overlap'] for z in exports])
        hf_overlap=np.zeros(len(theta),bool);lf_overlap=overlap.copy();matches={}
        if overlap.any():
            rel=d.replace('__','/') if '__' in d else 'core/'+d
            files=list((ST/'data'/rel).rglob('train_l*.npz'))
            assert files,'Cannot independently audit this layout'
            levels={int(re.fullmatch(r'train_l(\d+)\.npz',p.name).group(1)):p for p in files}
            lf_overlap[:]=False
            for level,p in levels.items():
                x=np.load(p)['x'].astype(np.float32)
                ids=[np.flatnonzero(np.all(x==row,axis=1)).tolist() for row in theta]
                hit=np.asarray([bool(i) for i in ids])
                if level==max(levels):hf_overlap|=hit
                else:lf_overlap|=hit
                matches[str(level)]=ids
            assert np.array_equal(overlap,hf_overlap|lf_overlap)
        write_json(ROOT/'input_audits'/f'{d}.json',dict(dataset=d,n=len(theta),
            hf_train_overlap=hf_overlap.tolist(),lf_train_overlap=lf_overlap.tolist(),
            strict_eligible=not overlap.any(),matches_by_training_level=matches,
            note='Overlap is defined in the float32 condition vectors actually passed to base models; answers are not inspected.'))
        print(d,'HF overlap',int(hf_overlap.sum()),'LF overlap',int(lf_overlap.sum()),flush=True)

if __name__=='__main__':main()
