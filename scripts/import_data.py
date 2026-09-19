#!/usr/bin/env python3
"""Restore checksum-verified numerical files from the offline data companion."""
import argparse
import fnmatch
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import tempfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def destination(name):
    relative = PurePosixPath(name)
    if relative.is_absolute() or '..' in relative.parts or '\\' in name:
        raise ValueError('Unsafe manifest path')
    path = ROOT.joinpath(*relative.parts)
    if not path.resolve().is_relative_to(ROOT.resolve()):
        raise ValueError('Destination escapes the artifact directory')
    return path


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--archive', type=Path, required=True)
    p.add_argument('--group', choices=['all', 'analysis', 'datasets', 'campaigns', 'results'], default='all')
    p.add_argument('--include', help='Optional path glob, e.g. datasets/core/heat_generated/*')
    args = p.parse_args()
    manifest = json.loads((ROOT / 'data_manifest.json').read_text())
    records = [r for r in manifest['files']
               if (args.group == 'all' or r['path'].startswith(args.group + '/'))
               and (args.include is None or fnmatch.fnmatchcase(r['path'], args.include))]
    if not records:
        raise SystemExit('No files match the requested group or pattern.')
    restored = 0
    present = 0
    with zipfile.ZipFile(args.archive) as archive:
        for record in records:
            target = destination(record['path'])
            if target.is_file() and target.stat().st_size == record['bytes'] and digest(target) == record['sha256']:
                present += 1
                continue
            key = 'objects/' + record['sha256']
            if archive.getinfo(key).file_size != record['bytes']:
                raise RuntimeError('Unexpected object size: ' + record['path'])
            target.parent.mkdir(parents=True, exist_ok=True)
            descriptor, tmp = tempfile.mkstemp(prefix='.import-', dir=target.parent)
            temp_path = Path(tmp)
            try:
                h = hashlib.sha256()
                with os.fdopen(descriptor, 'wb') as output, archive.open(key) as source:
                    for block in iter(lambda: source.read(8 * 1024 * 1024), b''):
                        h.update(block)
                        output.write(block)
                if h.hexdigest() != record['sha256']:
                    raise RuntimeError('Checksum mismatch: ' + record['path'])
                temp_path.replace(target)
                restored += 1
            finally:
                temp_path.unlink(missing_ok=True)
    print(json.dumps({'restored': restored, 'already_verified': present,
                      'group': args.group, 'matched': len(records)}, indent=2))


if __name__ == '__main__':
    main()
