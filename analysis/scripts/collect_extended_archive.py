"""Read-only inventory of the wider historical, correction, and budget archives."""
import io,json,subprocess,zipfile
from pathlib import Path
from build_data import ROOT,load

def main():
    names=sorted(load(ROOT/'data/individual_model_summary.json')['means'])
    code=r'''
from pathlib import Path
import collections,csv,hashlib,io,json,sys,zipfile
import numpy as np
root=Path('/archive/mf_field');v2=root.parent/'mf_field_v2'
names=__NAMES__;payload={};inv={}
def add(path,name):
    if path.exists():payload[name]=path.read_bytes()
for rel in ['operator_library/MODEL_CATALOG.md','operator_library/results/bench_full_metrics.csv','operator_library/results/FINDINGS.md',
            'operator_library/results/SUBSET_COMPARISON.md','experiments/bench_ct/results/ct_metrics.csv',
            'experiments/bench_ct/results/hfonly_vs_film.csv','experiments/wp1/HINDSIGHT.md',
            'experiments/wp1/state/hindsight.csv','experiments/wp3/WP3_REPORT.md']:
    add(root/rel,rel)
for rel in ['experiments/bench_ct/raw','experiments/bench_ct/raw_hfonly','experiments/bench_ct/raw_film']:
    counts=collections.Counter();files=sorted((root/rel).glob('*.json'))
    for p in files:
        d=json.loads(p.read_text());counts[d.get('model','?')]+=1
        ds=d.get('dataset','')
        if ds in names and (d.get('seed')==42 or p.stem.endswith('__s42')):add(p,rel+'/'+p.name)
    inv[rel]=dict(files=len(files),model_counts=dict(counts))
for ds in names:
    for p in (root/'operator_library/results/raw_full').glob('transolver_residual__'+ds+'__*s42.json'):add(p,'operator_library/results/raw_full/'+p.name)
    add(root/'operator_library/results/reeval_transolver'/f'{ds}.json','operator_library/results/reeval_transolver/'+ds+'.json')
rows=list(csv.DictReader((root/'operator_library/results/bench_full_metrics.csv').open()))
inv['operator_library']=dict(rows=len(rows),datasets=sorted({r['dataset'] for r in rows}),model_counts=dict(collections.Counter(r['model'] for r in rows)),
                 transolver_val_based=sum(r['model']=='transolver_residual' and r['val_based']=='1' for r in rows))
variants=[]
for family in ['core','ext','sharp']:
    for p in sorted((v2/family).glob('*_lfabund')):
        rec=dict(path=str(p.relative_to(v2)),meta_exists=(p/'meta.json').exists(),levels={})
        add(p/'meta.json','v2/'+str(p.relative_to(v2))+'/meta.json')
        for f in sorted(p.glob('train_l*.npz')):
            with zipfile.ZipFile(f) as z,z.open('x.npy') as stream:
                version=np.lib.format.read_magic(stream)
                shape,order,dtype=(np.lib.format.read_array_header_1_0(stream) if version==(1,0) else np.lib.format.read_array_header_2_0(stream))
            rec['levels'][f.stem]=list(shape)
        variants.append(rec)
inv['coarse_abundant']=variants
inv['budget_directories']={p.name:len(list(p.glob('N*_s*'))) for p in (v2/'budgets').iterdir() if p.is_dir()}
counts=collections.Counter();raw=list((root/'experiments/wp1/raw').glob('*.json'))
for p in raw:
    d=json.loads(p.read_text());counts[d.get('model','?')+(' / LF4000' if 'lfabund' in p.name else ' / original LF')]+=1
inv['wp1']=dict(raw_jsons=len(raw),coarse_abundant_results=sum('lfabund' in p.name for p in raw),model_counts=dict(counts))
inv['source_hashes']={name:hashlib.sha256(b).hexdigest() for name,b in payload.items()}
payload['inventory.json']=json.dumps(inv,indent=2).encode()
b=io.BytesIO()
with zipfile.ZipFile(b,'w',zipfile.ZIP_DEFLATED) as z:
    for name,value in payload.items():z.writestr(name,value)
sys.stdout.buffer.write(b.getvalue())
'''.replace('__NAMES__',repr(names))
    p=subprocess.run(['ssh','-o','BatchMode=yes','-o','ConnectTimeout=15','login006',
        '/archive/mf_field/factory_mffp/.venv/bin/python -'],input=code.encode(),capture_output=True,timeout=300)
    if p.returncode:raise RuntimeError(p.stderr.decode())
    out=ROOT/'data/extended_archive';out.mkdir(exist_ok=True)
    with zipfile.ZipFile(io.BytesIO(p.stdout)) as z:
        for name in z.namelist():
            f=out/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_bytes(z.read(name))
    d=load(out/'inventory.json')
    print('Historical archive:',len(d['operator_library']['datasets']),'dataset names;',d['operator_library']['model_counts'])
    print('Coarse-abundant variants:',len(d['coarse_abundant']),'WP1:',d['wp1'])

if __name__=='__main__':main()
