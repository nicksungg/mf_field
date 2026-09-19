import json
from config import ROOT,sha

def verify():
    source=json.loads((ROOT/'SOURCE.json').read_text())
    for name,h in source.items():assert sha(ROOT/name)==h,('Frozen file changed',name)

if __name__=='__main__':verify()
