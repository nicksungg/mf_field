#!/usr/bin/env python3
"""Maintainer command: refresh checksums after intentional release-file changes.

Run only in a full LFS checkout. Ignored runtime/output files are excluded.
Scientific archives are hashed, never modified.
"""
import hashlib
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def digest(path):
    value = hashlib.sha256()
    with path.open('rb') as stream:
        start = stream.read(1024)
        if start.startswith(b'version https://git-lfs.github.com/spec/v1\n'):
            raise RuntimeError(f'Unfetched LFS pointer: {path}. Run git lfs pull first.')
        value.update(start)
        for block in iter(lambda: stream.read(8 * 1024 * 1024), b''):
            value.update(block)
    return value.hexdigest()


def main():
    names = subprocess.check_output(['git', 'ls-files', '--cached', '--others', '--exclude-standard', '-z'], cwd=ROOT)
    files = []
    for name in sorted(set(names.decode().split('\0')) - {'', 'release_manifest.json', 'MANIFEST.sha256'}):
        path = ROOT / name
        if path.is_file():
            files.append(dict(path=name, bytes=path.stat().st_size, sha256=digest(path)))
    manifest = json.loads((ROOT / 'release_manifest.json').read_text())
    manifest.update(release='AutoMF code, datasets and results', manuscript_included=False,
                    files=files, file_count=len(files), bytes_uncompressed=sum(r['bytes'] for r in files))
    (ROOT / 'release_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    lines = [f'{r["sha256"]}  {r["path"]}' for r in files]
    lines.append(f'{digest(ROOT / "release_manifest.json")}  release_manifest.json')
    (ROOT / 'MANIFEST.sha256').write_text('\n'.join(lines) + '\n')
    print(f'Manifest refreshed: {len(files)} files, {manifest["bytes_uncompressed"]:,} bytes')


if __name__ == '__main__':
    main()
