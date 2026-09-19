"""Freeze the complete runnable campaign before submission."""
from baseline_common import ROOT, sha, write_json


def main():
    names = list(ROOT.glob('*.py')) + list(ROOT.glob('*.sbatch'))
    for folder in ['vendor', 'common', 'data_adapters', 'tests']:
        names += [p for p in (ROOT / folder).rglob('*')
                  if p.is_file() and '__pycache__' not in p.parts
                  and p.suffix in ('.py', '.json', '.patch')]
    names += [ROOT / n for n in ['PLAN.json', 'ROLES.json', 'BASELINES.json',
              'INPUT_MANIFEST.json', 'INPUT_AUDIT.json', 'prior_training_mean.json',
              'PAPER_VENDOR_SOURCES.json'] if (ROOT / n).exists()]
    write_json(ROOT / 'SOURCE.json', {str(p.relative_to(ROOT)): sha(p) for p in sorted(set(names))})
    print('Frozen', len(set(names)), 'source and protocol files.')


if __name__ == '__main__':
    main()
