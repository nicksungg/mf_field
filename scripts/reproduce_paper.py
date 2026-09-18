#!/usr/bin/env python3
"""Rebuild numerical tables and figures from bundled predictions and statistics."""
import argparse,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
p=argparse.ArgumentParser(description=__doc__);p.add_argument('--pdf',action='store_true');a=p.parse_args()
subprocess.run(['make','data'],cwd=ROOT/'paper',check=True)
if a.pdf:
    subprocess.run(['make','all'],cwd=ROOT/'paper',check=True)
    subprocess.run([sys.executable,'scripts/verify_paper.py'],cwd=ROOT/'paper',check=True)
print('Rebuilt tables, figures and numerical checks in paper/.')
