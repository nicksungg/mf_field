from campaign_common import *

def main():
 names=['PLAN.json','ROLES.json','TASKS.json','COVERAGE.json','REUSE.json']
 names += [str(p.relative_to(ROOT)) for p in ROOT.glob('*.py')]
 for folder in ['vendor','common','data_adapters']:
  names += [str(p.relative_to(ROOT)) for p in (ROOT/folder).rglob('*') if p.is_file() and p.suffix in ['.py','.json'] and '__pycache__' not in p.parts]
 entries={p:sha(ROOT/p) for p in sorted(set(names))};path=ROOT/'SOURCE.json'
 if path.exists():assert json.loads(path.read_text())==entries
 else:write_json(path,entries)
 print('FROZEN',len(entries),'source/config files')
if __name__=='__main__':main()
