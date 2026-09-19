"""Fit mixtures on calibration answers, seal weights, then evaluate identical cases."""
import argparse,csv
from campaign_common import *
from ensemble_rules import gram,fit_auto

def load_prediction(ds,model,info):
 path=ROOT/'predictions'/ds/f'{model}.npz';meta=ROOT/'metadata'/ds/f'{model}.json'
 record=json.loads(meta.read_text())
 if record.get('smoke',False) or record.get('scientific_result') is False:raise ValueError('Smoke output cannot be scored')
 assert record['prediction_sha256']==sha(path),(ds,model,'prediction changed')
 with np.load(path,allow_pickle=False) as z:
  x=z['X'] if 'X' in z else z['theta'];pred=z['pred'].astype(np.float64);grid=z['work_grid'].tolist()
 with np.load(ROOT/'data'/ds/f"test_l{info['hf_level']}.npz") as z:query=z['x']
 np.testing.assert_array_equal(x,query)
 assert grid==info['work_grid'] and pred.shape==(len(query),int(np.prod(grid))) and np.isfinite(pred).all()
 return pred

def relative_errors(pred,target):
 return np.linalg.norm(pred-target,axis=1)/np.maximum(np.linalg.norm(target,axis=1),1e-8)

def collect_dataset(ds,plan,roles):
 info=plan['datasets'][ds];pred=np.stack([load_prediction(ds,m,info) for m in MODELS],axis=1)
 specs=[roles[f'{ds}__s{s}'] for s in SEEDS];fits={};digests={m:sha(ROOT/'predictions'/ds/f'{m}.npz') for m in MODELS}
 # No evaluation answer file is opened until EVERY partition's weights are fixed.
 for spec in specs:
  seed=spec['seed'];path=ROOT/'answers'/ds/f's{seed}/calibration.npz';assert sha(path)==spec['calibration_sha256']
  with np.load(path) as z:target=z['target'].astype(np.float64);rows=z['query_rows'].tolist()
  assert rows==spec['calibration_pool'];lookup={r:i for i,r in enumerate(rows)}
  for budget,selected in spec['budgets'].items():
   g=gram(pred[selected],target[[lookup[r] for r in selected]])
   weights,selection=fit_auto(g)
   for w in weights.values():assert (w>=-1e-10).all() and abs(w.sum()-1)<1e-6
   fits[f's{seed}_K{budget}']=dict(seed=seed,budget=int(budget),actual_calibration_count=len(selected),query_rows=selected,weights={m:w.tolist() for m,w in weights.items()},selection=selection)
 locked=dict(dataset=ds,model_order=MODELS,fits=fits,prediction_sha256=digests,plan_sha256=sha(ROOT/'PLAN.json'),roles_sha256=sha(ROOT/'ROLES.json'),evaluation_answers_used=False)
 lockpath=ROOT/'weights'/f'{ds}.json'
 if lockpath.exists():assert json.loads(lockpath.read_text())==locked,'Existing weights conflict'
 else:write_json(lockpath,locked)
 baseline_pred={};baseline_err={};baseline_artifacts={}
 for model in BASELINES:
  ep=ROOT/'baseline_errors'/ds/f'{model}.json'
  if ep.exists():
   e=json.loads(ep.read_text());values=np.asarray(e['per_query_rel_l2'],np.float64)
   assert values.shape==(info['n_query'],) and np.isfinite(values).all() and (values>=0).all()
   assert e['dataset']==ds and e['model']==model
   assert e['query_sha256']==info['query_sha256'] and e['work_grid']==info['work_grid'], 'Baseline error identities or grid differ'
   if e.get('smoke',False) or e.get('scientific_result') is False:raise ValueError('Non-scientific baseline error cache')
   baseline_err[model]=values
   baseline_artifacts[model]=dict(kind='per_case_errors',scalar_errors_sha256=sha(ep),query_sha256=e['query_sha256'],work_grid=e['work_grid'])
  else:
   baseline_pred[model]=load_prediction(ds,model,info)
   baseline_artifacts[model]=dict(kind='prediction',prediction_sha256=sha(ROOT/'predictions'/ds/f'{model}.npz'),metadata_sha256=sha(ROOT/'metadata'/ds/f'{model}.json'))
 records=[]
 for spec in specs:
  seed=spec['seed'];path=ROOT/'answers'/ds/f's{seed}/evaluation.npz';assert sha(path)==spec['evaluation_sha256']
  with np.load(path) as z:target=z['target'].astype(np.float64);rows=z['query_rows'].tolist()
  assert rows==spec['evaluation']
  def append(model,kind,errors,budget=None):
   records.append(dict(dataset=ds,partition=seed,model=model,kind=kind,budget=budget,n_eval=len(rows),query_rows=rows,mean_rel_l2=float(np.mean(errors)),per_case_rel_l2=np.asarray(errors).tolist()))
  for j,model in enumerate(MODELS):append(model,'individual',relative_errors(pred[rows,j],target))
  for model in BASELINES:
   e=baseline_err[model][rows] if model in baseline_err else relative_errors(baseline_pred[model][rows],target)
   append(model,'baseline',e)
  for budget in spec['budgets']:
   for method,w in fits[f's{seed}_K{budget}']['weights'].items():
    blended=np.einsum('nmp,m->np',pred[rows],np.asarray(w),optimize=True)
    append(method,'ensemble',relative_errors(blended,target),int(budget))
 output=dict(dataset=ds,complete=True,n_individual_models=9,n_baseline_entries=len(BASELINES),model_order=MODELS,baseline_alias=plan['baseline_alias'],baseline_artifacts=baseline_artifacts,work_grid=info['work_grid'],n_base_hf_train=info['n_base_hf_train'],weight_sha256=sha(lockpath),records=records,protocol=plan['protocol'])
 write_json(ROOT/'results'/f'{ds}.json',output)
 print('COLLECTED',ds,len(records),'rows',flush=True)
 return output

def main():
 ap=argparse.ArgumentParser();ap.add_argument('--dataset');ap.add_argument('--aggregate',action='store_true');a=ap.parse_args();verify_source();plan=json.loads((ROOT/'PLAN.json').read_text());roles=json.loads((ROOT/'ROLES.json').read_text())
 if a.aggregate:
  assert len(plan['datasets'])==4,'Completion aggregate requires exactly 25 datasets'
  allrows=[]
  for ds in plan['datasets']:
   obj=json.loads((ROOT/'results'/f'{ds}.json').read_text());assert obj['complete'];allrows+=obj['records']
  path=ROOT/'results/comparison.csv'
  with path.open('w') as f:
   cols=['dataset','partition','model','kind','budget','n_eval','mean_rel_l2'];w=csv.DictWriter(f,fieldnames=cols);w.writeheader();w.writerows({k:r[k] for k in cols} for r in allrows)
  write_json(ROOT/'results/COMPLETE.json',dict(complete=True,datasets=list(plan['datasets']),n_datasets=4,n_individual_predictions=36,n_baseline_entries=52,plan_sha256=sha(ROOT/'PLAN.json'),comparison_sha256=sha(path),baseline_alias=plan['baseline_alias']))
 else:
  for ds in ([a.dataset] if a.dataset else plan['datasets']):collect_dataset(ds,plan,roles)
if __name__=='__main__':main()
