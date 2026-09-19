"""Frozen campaign identities and atomic artifacts."""
from pathlib import Path
import hashlib,json,os
import numpy as np
ROOT=Path(__file__).resolve().parent
MF=Path('/archive/mf_field')
ST=MF/'experiments/st_bench/data'
DIRECT=['mf_fno_transfer_film','mf_fno_allpairs','convnext_unet_film','fno_fire_distcond','wno_transfer_film','mf_deeponet','st_hf_pod_gp']
MODELS=DIRECT+['uqcorr_transolver_pred','uqcorr_convnext_pred']
BASELINES=['st_koh_pod','st_nargp_pod','st_mfdnn','st_mfdeeponet','st_dmfal','nomad_mf','mfrnp','fno_coregionalization','mf_fno_transfer','mf_fno_transfer_bar','st_lf_affine_pod','st_knn','st_mean']
SEEDS=[71,172,273]
EXCLUDE='node2900,node4200,node2901,node4002'
def sha(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(4*1024*1024),b''):h.update(b)
 return h.hexdigest()
def write_json(path,value):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_name(path.name+f'.tmp.{os.getpid()}');tmp.write_text(json.dumps(value,indent=2,allow_nan=False)+'\n');os.replace(tmp,path)
def save_npz(path,**arrays):
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True);tmp=path.with_name(path.name+f'.tmp.{os.getpid()}')
 with tmp.open('wb') as f:np.savez_compressed(f,**arrays)
 os.replace(tmp,path)
def keys(x):
 x=np.asarray(x,np.float32).copy();x[x==0]=0
 return [np.ascontiguousarray(r).tobytes() for r in x]
def verify_source():
 for name,digest in json.loads((ROOT/'SOURCE.json').read_text()).items():
  if sha(ROOT/name)!=digest:raise ValueError('Source changed: '+name)
def roster():
 core=['poisson_local','heat_generated','heat_local','darcy_generated','fluid','era5','poisson_generated_v2','lid_driven_cavity_v2','ifc_heat','ifc_poisson']
 ext=['helmholtz_2d','rayleigh_benard_2d','wave_2d','eikonal_2d','cahn_hilliard_2d','pressure_poisson_poiseuille']
 sharp=['euler','burgers_2d','shallow_water_2d','porous_medium_2d','helmholtz_2d','cahn_hilliard','fisher_kpp_2d','allen_cahn_2d','phase_field_crystal_2d']
 out={d:dict(source=str(ST/'core'/d),group='core') for d in core}
 out.update({g+'__'+d:dict(source=str(ST/g/d),group=g) for g,ds in [('ext',ext),('sharp',sharp)] for d in ds})
 out['poisson_generated_v2']['source']='/archive/mf_field_v2/core/poisson_generated_v2'
 out['lid_driven_cavity_v2']['source']='/archive/mf_field_v2/core/lid_driven_cavity_generated'
 for d,geom,mat in [('poisson_local','legacy_2x2',True),('ifc_poisson','standard_2x1',False)]:
  out[d]['repair']=dict(source_geometry=geom,legacy_matrix=mat,rhs_dx2=True)
 assert len(out)==25
 return out
