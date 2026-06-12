"""One-shot benchmark status reporter (file-output friendly)."""
import glob, os, subprocess
from collections import Counter

ROOT = "/orcd/data/faez/001/nick/mf_field/factory_mffp"
os.chdir(ROOT)
fams = ["fno_mf_stack","fno_coregionalization","fno_coreg_residual","fno_coreg_conditioned","fno_coreg_lf_hf_transfer",
        "transolver_residual","transolver_attention_fusion","v9_baseline",
        "mfrnp","mf_deeponet","d_mfd","mf_fno_transfer","mf_fno_transfer_2m","mf_fno_transfer_film","fno_additive","fno_autoregressive","fno_multilevel"]
dss = ["ifc_heat","ifc_poisson","poisson_local","heat_local","fluid","era5",
       "pm_test","advection_diffusion_generated","allen_cahn_generated",
       "burgers_generated","burgers_param_generated","darcy_generated",
       "heat_generated","lid_driven_cavity_generated","poisson_generated"]
allc = {f"{f}__{d}" for f in fams for d in dss}
done = {os.path.basename(p).replace("__e2500__s42.json","")
        for p in glob.glob("results/raw_bench/*__e2500__s42.json")}
q = subprocess.run("squeue -u nicksung -h -o %j", shell=True,
                   stdout=subprocess.PIPE).stdout.decode().split()
qnames = set(n[2:] for n in q if n.startswith("b_"))
pif = subprocess.run("squeue -u nicksung -h -o '%P %j'", shell=True,
                     stdout=subprocess.PIPE).stdout.decode().splitlines()
pifaez = sum(1 for l in pif if " b_" in l and "pi_faez" in l)
drips = subprocess.run("ps -u nicksung -o cmd | grep -c '[d]rip_submit.sh'",
                       shell=True, stdout=subprocess.PIPE).stdout.decode().strip()
miss = sorted(allc - done - qnames)
print("done=%d/135" % len(done))
print("queued_unique=%d  drips=%s  pifaez_mine=%d" % (len(qnames), drips, pifaez))
print("missing=%s" % miss)
c = Counter(n.split("__")[0] for n in done)
for f in fams:
    print("  %-30s %d/15" % (f, c.get(f, 0)))
