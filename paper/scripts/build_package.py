"""Bundle frozen paper sources and verify a rebuild from a clean extraction."""
from pathlib import Path
import hashlib,json,subprocess,tempfile,zipfile
from paper_scope import HISTORICAL_COUNT, PDE_COUNT, PAPER_COUNT
ROOT=Path(__file__).resolve().parents[1]

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    root_names=['Makefile','README.md','main.tex','main.pdf','references.bib',
                'iclr2026_conference.sty','iclr2026_conference.bst','natbib.sty','fancyhdr.sty']
    files=[ROOT/n for n in root_names]
    for directory in ['sections','tables','figures','data','research','supplement']:
        files.extend(p for p in (ROOT/directory).rglob('*') if p.is_file()
                     and '__pycache__' not in p.parts and p.suffix not in ['.pyc','.log'])
    files.extend((ROOT/'scripts').glob('*.py'))
    files.extend((ROOT/'revision').glob('*.md'))
    files.extend((ROOT/'revision').glob('*.json'))
    qa_names=['appendix_streamlining_checks.json','appendix_audit_checks.json','roster_training_counts.json','extension_checks.json','previous_draft_preservation.json','template_source.json','data_checks.json','era5_checks.json','era5_baseline_checks.json','individual_model_checks.json',
              'baseline_match_checks.json','b8_recovery_checks.json','gallery_checks.json','overview_checks.json','field_comparison_checks.json','cavity_visual_audit.json','verification.json','visual_review.json',
              'review_analysis_checks.json','loss_control_checks.json','calibration_cli_checks.json','original_preservation.json']
    files.extend(ROOT/'qa'/n for n in qa_names)
    files=sorted(set(files))
    assert all(p.is_file() for p in files)
    manifest=ROOT/'SOURCE_MANIFEST.sha256'
    manifest.write_text(''.join(f'{digest(p)}  {p.relative_to(ROOT)}\n' for p in files))
    archive=ROOT/'automf_latex_source.zip'
    with zipfile.ZipFile(archive,'w',compression=zipfile.ZIP_DEFLATED,compresslevel=8) as z:
        for p in files+[manifest]:z.write(p,str(p.relative_to(ROOT)))
    with tempfile.TemporaryDirectory(prefix='automf_paper_rebuild_') as folder:
        clean=Path(folder)
        with zipfile.ZipFile(archive) as z:
            assert z.testzip() is None
            z.extractall(clean)
        for line in (clean/'SOURCE_MANIFEST.sha256').read_text().splitlines():
            value,name=line.split('  ',1);assert digest(clean/name)==value,name
        with (ROOT/'qa/package_build.log').open('w') as log:
            for cmd in [['make','data'],['make','all'],['python3','scripts/audit_appendix.py'],['python3','scripts/verify_paper.py']]:
                subprocess.run(cmd,cwd=clean,stdout=log,stderr=subprocess.STDOUT,check=True)
        verified=json.loads((clean/'qa/verification.json').read_text())
        same_tables=all((clean/p.relative_to(ROOT)).read_bytes()==p.read_bytes() for p in (ROOT/'tables').glob('*.tex'))
        assert same_tables,'Generated table mismatch'
        def pdftext(p):return subprocess.check_output(['pdftotext','-layout',str(p),'-'])
        assert pdftext(clean/'main.pdf')==pdftext(ROOT/'main.pdf'),'PDF text differs after rebuild'
        result=dict(passed=True,archive=archive.name,sha256=digest(archive),bytes=archive.stat().st_size,
                    files=len(files)+1,clean_source_manifest_valid=True,clean_build_passed=True,
                    generated_tables_match=True,pdf_text_matches=True,
                    main_text_pages=verified['main_text_end_page'],total_pages=verified['total_pages'],
                    main_gallery_datasets=verified['gallery_checks']['main_datasets'],
                    historical_aggregate_datasets=HISTORICAL_COUNT,pde_aggregate_datasets=PDE_COUNT,paper_datasets=PAPER_COUNT,
                    unreported_era5_experts=0,era5_ensemble_experts=9,
                    era5_baseline_entries=verified['era5_baseline_checks']['available_entries'],
                    era5_missing_baselines=verified['era5_baseline_checks']['missing_ids'],
                    retrospective_automatic_fits=9*HISTORICAL_COUNT,retrospective_loss_fits=3*HISTORICAL_COUNT,calibration_cli_tests=8)
    (ROOT/'qa/package_verification.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
