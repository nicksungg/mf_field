import sys, os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import numpy as np, time
from lid_driven_cavity import solve_cavity, STEADY_TOL, MAX_STEPS
print(f"MAX_STEPS={MAX_STEPS} TOL={STEADY_TOL}", flush=True)
for Re,n in [(1000,256),(100,256),(1000,128)]:
    t=time.time(); omega,steps,resid=solve_cavity(Re,n); wt=time.time()-t
    print(f"Re={Re} n={n}: steps={steps} resid={resid:.2e} conv={resid<STEADY_TOL} walltime={wt:.0f}s", flush=True)
