#!/usr/bin/env python3
"""Check the source-only publication tree, optionally using a PRIVATE literal denylist."""
import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN = {'.xp3', '.exe', '.dll', '.ipa', '.p12', '.p8', '.key', '.pem',
             '.mobileprovision', '.ksd', '.bmp', '.png', '.jpg', '.jpeg', '.mp4',
             '.wmv', '.ogg', '.wav', '.ttf', '.otf', '.zip', '.log', '.pyc'}
PATTERNS = [
    re.compile(r'/(?:Users|home)/[^\s/]+/'),
    re.compile(r'gh[pousr]_[A-Za-z0-9]{20,}'),
    re.compile(r'github_pat_[A-Za-z0-9_]{20,}'),
    re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
    re.compile(r'\b[A-Fa-f0-9]{8}-[A-Fa-f0-9]{16}\b'),
]

def inspect(root, private_literals=()):
    errors = []
    files = []
    for p in sorted(root.rglob('*')):
        rel = p.relative_to(root)
        if '.git' in rel.parts:
            continue
        if p.is_symlink():
            errors.append(f'{rel}: symlink is not permitted'); continue
        if not p.is_file(): continue
        files.append(str(rel))
        if p.suffix.lower() in FORBIDDEN:
            errors.append(f'{rel}: forbidden binary/private/generated extension')
        if any(part in {'.local', '__pycache__', 'xcuserdata', 'DerivedData', 'Saves', 'Game'} for part in rel.parts):
            errors.append(f'{rel}: generated or user-data directory')
        try:
            body = p.read_text(encoding='utf-8-sig')
        except UnicodeError:
            errors.append(f'{rel}: not UTF-8 source text'); continue
        if '\x00' in body: errors.append(f'{rel}: binary data')
        if any(pattern.search(body) for pattern in PATTERNS):
            errors.append(f'{rel}: possible credential or personal path')
        text = (str(rel) + '\n' + body).casefold()
        if any(item.casefold() in text for item in private_literals if item):
            errors.append(f'{rel}: private denylist match (value not printed)')
    return files, errors

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    parser.add_argument('--deny-file', type=Path, help='PRIVATE JSON list of names/IDs; never add it to this repository')
    args = parser.parse_args()
    literals = json.loads(args.deny_file.read_text()) if args.deny_file else []
    if not isinstance(literals, list) or not all(isinstance(x, str) for x in literals):
        parser.error('Denylist must be a JSON list of strings')
    files, errors = inspect(args.root.resolve(), literals)
    if errors:
        print('\n'.join(errors)); raise SystemExit(1)
    print(f'PASS: {len(files)} source-only files; no configured privacy/content findings.')
    print('This is a heuristic scan, not a legal or complete secret-scanning guarantee.')

if __name__ == '__main__': main()
