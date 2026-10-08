#!/usr/bin/env python3
"""Audit compiler-extracted keys and report intentionally preserved technical text."""
import argparse
import json
import pathlib
import plistlib
import re
import subprocess

ROOT = pathlib.Path(__file__).resolve().parents[1]
PLACEHOLDER = re.compile(r'%(?:\d+\$)?[-+0#]*\d*(?:\.\d+)?(?:hh|ll|h|l|z|t|j)?[@diuoxXfFeEgGcsp]')

def preserved(key):
    if key == 'Safari':
        return True
    remainder = PLACEHOLDER.sub('', key)
    remainder = re.sub(r'\b(?:MB|GB)\b', '', remainder)
    return not re.search(r'[A-Za-z\u4e00-\u9fff]', remainder)

def audit(directory):
    resource = ROOT / 'purge/zh-Hans.lproj/Localizable.strings'
    strings = plistlib.loads(subprocess.check_output(['plutil', '-convert', 'xml1', '-o', '-', str(resource)]))
    keys = {}
    for path in directory.glob('*.stringsdata'):
        data = json.loads(path.read_text())
        for entry in data.get('tables', {}).get('Localizable', []):
            keys.setdefault(entry['key'], set()).add(pathlib.Path(data['source']).name)
    missing = {key: sorted(files) for key, files in sorted(keys.items()) if key not in strings and not preserved(key)}
    return {
        'chineseDisplayEntryCount': len(strings),
        'compilerExtractedKeyCount': len(keys),
        'compilerKeysWithChineseResources': len(keys.keys() & strings.keys()),
        'intentionallyPreservedCompilerKeys': sorted(key for key in keys if key not in strings and preserved(key)),
        'untranslatedDisplayCompilerKeys': missing,
        'scope': 'Main app compiler-emitted Localizable keys, supplemented by explicit dynamic label and native getter tests. User names, file paths, identifiers, commands, and system/library diagnostics retain their original values.',
    }

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('directory', type=pathlib.Path)
    parser.add_argument('--report', type=pathlib.Path)
    args = parser.parse_args()
    result = audit(args.directory)
    text = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.report:
        args.report.write_text(text)
    print(text, end='')
    raise SystemExit(bool(result['untranslatedDisplayCompilerKeys']))
