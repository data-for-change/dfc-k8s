#!/usr/bin/env python3
import sys
import json
import subprocess
import functools


@functools.lru_cache()
def get_vault_path(path):
    return json.loads(subprocess.check_output([
        'vault', 'kv', 'get', '-format=json', f'kv/{path}'
    ]))['data']['data']


def get_vault_val(val):
    _, path, key = val.split(":")
    key = key.replace('~"', '')
    return '"' + get_vault_path(path)[key] + '"'


def main(filename):
    with open(filename) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            name, val = line.split('=', 1)
            if "~vault:" in val:
                val = get_vault_val(val)
            print(f'{name}={val}')


if __name__ == '__main__':
    main(*sys.argv[1:])
