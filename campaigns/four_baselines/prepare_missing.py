"""Import the four completed libraries and baseline cells valid on current definitions."""
import shutil
from campaign_common import *
from baseline_worker import alias_evidence
OLD=MF/'experiments/complete25_20260915'
RELEASE=MF/'release/mf_field_surrogate_bench'
FULL=MF/'release/predictions_full'
FOUR=['sharp__cahn_hilliard','sharp__fisher_kpp_2d','sharp__allen_cahn_2d','sharp__phase_field_crystal_2d']
PAPER=['nomad_mf','mfrnp','fno_coregionalization','mf_fno_transfer','mf_fno_transfer_bar']

def link_file(source,destination):
 destination.parent.mkdir(parents=True,exist_ok=True)
 if destination.exists():assert sha(source)==sha(destination);return
 destination.symlink_to(source.resolve())

def raw_result(ds,model,subdir):
 files=sorted((RELEASE/'results/raw_json'/subdir).glob(f'{model}__{ds}__*s42.json'))
 assert files,(ds,model,subdir)
 assert len(files)==1,(ds,model,files)
 return files[0],json.loads(files[0].read_text())

def save_errors(ds,model,info,raw_path,raw,proof):
 values=np.asarray(raw['splits']['test_hf']['rel_l2_per_sample'],np.float64)
 assert raw['model']==model and raw['dataset']==ds and not raw.get('excluded')
 assert values.shape==(info['n_query'],) and np.isfinite(values).all() and (values>=0).all()
 assert raw['work_grid']==info['work_grid']
 out=dict(dataset=ds,model=model,per_query_rel_l2=values.tolist(),query_sha256=info['query_sha256'],work_grid=info['work_grid'],n_query=info['n_query'],provenance=dict(raw_path=str(raw_path),raw_sha256=sha(raw_path),evidence=proof,training_hashes_available=False,historical_train_seconds=raw.get('train_seconds'),budget_note='Existing published-benchmark recipe and original training budget retained.'))
 write_json(ROOT/'baseline_errors'/ds/f'{model}.json',out)
 return dict(dataset=ds,model=model,status='reused',raw_path=str(raw_path),evidence=proof)

def main():
 plan=json.loads((ROOT/'PLAN.json').read_text());assert list(plan['datasets'])==FOUR
 records=[]
 for ds,info in plan['datasets'].items():
  for sub in ['data','answers']:
   dest=ROOT/sub/ds;dest.parent.mkdir(exist_ok=True)
   if not dest.exists():dest.symlink_to(OLD/sub/ds,target_is_directory=True)
  for m in MODELS:
   for sub,suffix in [('predictions','.npz'),('metadata','.json')]:link_file(OLD/sub/ds/(m+suffix),ROOT/sub/ds/(m+suffix))
  for m in BASELINES:
   if m not in PAPER:
    src=OLD/'baseline_errors'/ds/f'{m}.json';rec=json.loads(src.read_text());assert rec['query_sha256']==info['query_sha256']
    link_file(src,ROOT/'baseline_errors'/ds/f'{m}.json');records.append(dict(dataset=ds,model=m,status='reused',proof='Matching source training and test file hashes'))
  with np.load(ROOT/'data'/ds/f"test_l{info['hf_level']}.npz") as z:query=z['x'].astype(np.float32)
  with np.load(next(iter(info['source_test_files']))) as z:
   assert np.array_equal(query,z['x'].astype(np.float32));current_target=z['y'].astype(np.float32).reshape(len(query),-1)
  if ds=='sharp__cahn_hilliard':
   for m in PAPER:
    path,raw=raw_result(ds,m,'reevaluated');archive=FULL/f'{m}__{ds}__s42.npz'
    with np.load(archive) as z:
     assert z['target'].shape==current_target.shape
     np.testing.assert_array_equal(z['target'],current_target.astype(np.float16))
     np.testing.assert_allclose(z['rel_l2_per_sample'],raw['splits']['test_hf']['rel_l2_per_sample'],rtol=1e-5,atol=1e-9)
    records.append(save_errors(ds,m,info,path,raw,dict(kind='Same manuscript standard: saved target rows plus pre-export error alignment',prediction_archive=str(archive),prediction_sha256=sha(archive),current_hf_test_sha256=next(iter(info['source_test_files'].values())))))
  else:
   # Release README explicitly identifies legacy checkpoints for these three
   # datasets as incompatible. Only completed current-definition reruns qualify.
   for m in PAPER:
    paths=list((RELEASE/'results/raw_json/st_bench_reruns').glob(f'{m}__{ds}__*s42.json'))
    if not paths:continue
    path,raw=raw_result(ds,m,'st_bench_reruns')
    live=MF/'experiments/st_bench/raw_lb'/path.name;assert sha(live)==sha(path)
    assert ds=='sharp__fisher_kpp_2d' and query.shape[1]==50
    expected_params={'nomad_mf':211329,'mf_fno_transfer_bar':4743361};assert raw['n_params']==expected_params[m]
    records.append(save_errors(ds,m,info,path,raw,dict(kind='Completed current-definition rerun, documented by release and original training launcher; current test row order preserved by loader',live_result=str(live),live_result_sha256=sha(live),conditioning_dimension=50,release_documentation_sha256=sha(RELEASE/'results/README.md'),launcher_sha256=sha(MF/'experiments/st_bench/run_st_gpu.sbatch'),current_hf_test_sha256=next(iter(info['source_test_files'].values())))))
 # These two released transfer labels share exactly the same implementation.
 # Reuse the completed Fisher fit under both labels and disclose the alias.
 info=plan['datasets']['sharp__fisher_kpp_2d'];alias_evidence()
 original=ROOT/'baseline_errors/sharp__fisher_kpp_2d/mf_fno_transfer_bar.json';rec=json.loads(original.read_text());rec.update(model='mf_fno_transfer',alias_of='mf_fno_transfer_bar',independent_training=False,alias_evidence='Frozen architecture bytes and normalized executable recipe ASTs are identical')
 write_json(ROOT/'baseline_errors/sharp__fisher_kpp_2d/mf_fno_transfer.json',rec);records.append(dict(dataset='sharp__fisher_kpp_2d',model='mf_fno_transfer',status='alias',alias_of='mf_fno_transfer_bar'))
 tasks=[];coverage=[]
 for ds,info in plan['datasets'].items():
  for m in BASELINES:
   ep=ROOT/'baseline_errors'/ds/f'{m}.json';ready=ep.exists();coverage.append(dict(dataset=ds,model=m,status='reused' if ready else ('alias_after_transfer' if m=='mf_fno_transfer_bar' else 'needs_training')))
   if not ready and m!='mf_fno_transfer_bar':tasks.append(dict(dataset=ds,model=m))
 assert len(tasks)==10, tasks
 write_json(ROOT/'TASKS.json',tasks);write_json(ROOT/'COVERAGE.json',dict(datasets=FOUR,entries=coverage,reused_entries=40,total_baseline_entries=52,new_independent_fits=10,reused_expert_predictions=36,reason='Only current-definition gaps on Fisher KPP, Allen Cahn and phase field crystal. Existing paper21 remains unchanged.'))
 write_json(ROOT/'REUSE.json',dict(records=records,scope=plan['scope']))
 print('READY: 40/52 baseline entries reused; 10 fits fill remaining12 entries including2 aliases',flush=True)
if __name__=='__main__':main()
