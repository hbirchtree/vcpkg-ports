#!/usr/bin/env python3
from json import dumps, loads
from os import chdir
from os.path import dirname, exists
from subprocess import run, PIPE
from sys import argv


def git_tree_sha(port_name):
    git_result = run(
        ['git', 'rev-parse', f'HEAD:ports/{port_name}'],
        stdout=PIPE,
        encoding='utf-8')
    return git_result.stdout[:-1]


chdir(dirname(__file__))

port_name = argv[1]
port_prefix = f'{port_name[:1]}-'

if not exists(f'ports/{port_name}'):
    print(f'ERROR: Port {port_name} does not exist!')
    exit(1)

with open(f'ports/{port_name}/vcpkg.json') as manifest_data:
    manifest = loads(manifest_data.read())
    port_version = manifest['port-version']
    try:
        version = manifest['version']
    except KeyError:
        try:
            version = manifest['version-date']
        except KeyError:
            version = None
    try:
        sem_version = manifest['version-semver']
    except KeyError:
        sem_version = None

print(f':: Updating port {port_name}/{version}/{sem_version}#{port_version}')
git_tree = git_tree_sha(port_name)

version_file = f'versions/{port_prefix}/{port_name}.json'

version_object = {
    'port-version': port_version,
    'git-tree': git_tree,
}
if version is not None:
    version_object['version'] = version
if sem_version is not None:
    version_object['version-semver'] = sem_version

current = {
    'versions': [version_object]
}
if exists(version_file):
    with open(version_file, 'r+') as versioning:
        current = loads(versioning.read())
    for ver in current['versions']:
        if ver['port-version'] == port_version:
            print('Port version already in list')
            exit()
    current['versions'] = current['versions'] + [version_object]
with open(version_file, 'w+') as versioning:
    print(':: Appending to existing version list')
    versioning.truncate()
    versioning.write(dumps(current, indent=2))

baseline_file = f'versions/baseline.json'
baseline_object = {
    'baseline': sem_version or version,
    'port-version': port_version
}
current = {
    'default': {}
}
if exists(baseline_file):
    with open(baseline_file, 'r+') as baseline:
        current = loads(baseline.read())
    if port_name in current['default']:
        if current['default'][port_name]['port-version'] == port_version:
            print('Port version already in baseline')
            exit()
with open(baseline_file, 'w+') as baseline:
    print(':: Updating existing baseline')
    baseline.truncate()
    current['default'][port_name] = baseline_object
    baseline.write(dumps(current, indent=2))
