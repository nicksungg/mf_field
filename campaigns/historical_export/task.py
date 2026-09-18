import json
import sys
from config import ROOT,sha
from run import run

def main():
    contract=json.loads((ROOT/'GATE_LAUNCH.json').read_text())
    for file,expected in contract['source_sha256'].items():assert sha(ROOT/file)==expected,file
    assert sha(ROOT/'plan.json')==contract['plan_sha256']
    task=contract['tasks'][int(sys.argv[1])]
    run(**task)

if __name__=='__main__':main()
