#!/usr/bin/env python3
"""Check file integrity and completeness of the published dataset/model roster."""
import argparse,hashlib,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def sha(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(8*1024*1024),b''):h.update(b)
 return h.hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--quick',action='store_true');a=p.parse_args()
 inventory=json.loads((ROOT/'release_manifest.json').read_text());errors=[]
 for record in inventory['files']:
  path=ROOT/record['path']
  if not path.is_file():errors.append('Missing: '+record['path']);continue
  if path.stat().st_size!=record['bytes']:errors.append('Size: '+record['path']);continue
  if not a.quick and sha(path)!=record['sha256']:errors.append('SHA256: '+record['path'])
 datasets=json.loads((ROOT/'configs/datasets.json').read_text())
 assert len(datasets)==22
 for d,info in datasets.items():
  folder=ROOT/info['path'];tr=sorted(folder.glob('train_l*.npz'));te=sorted(folder.glob('test_l*.npz'))
  if not tr or len(tr)!=len(te):errors.append('Missing dataset levels: '+d)
 models=json.loads((ROOT/'configs/models.json').read_text());assert all(f'M{i}' in models for i in range(1,10))
 assert all(f'B{i}' in models for i in range(1,14))
 print(json.dumps({'passed':not errors,'files_checked':len(inventory['files']),
  'dataset_count':len(datasets),'library_models':9,'baseline_entries_including_controls':13,
  'mode':'size and presence' if a.quick else 'SHA256','errors':errors},indent=2))
 if errors:raise SystemExit(1)
if __name__=='__main__':main()
