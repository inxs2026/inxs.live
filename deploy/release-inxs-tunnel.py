#!/usr/bin/env python3
"""Render a tunnel-only Compose release from live inspect JSON on stdin.

Output contains credentials: redirect to a mode-0600 file, never logs.
Keeps the exact image, environment, TLS mounts, network and resource limits.
"""
import json
import sys


def release(inspected, revision):
    current = inspected[0]
    config = current['Config']
    host = current['HostConfig']
    command = list(config['Cmd'])
    if not command or command[0] != 'tunnel' or 'run' not in command:
        raise ValueError('Unexpected tunnel invocation')
    if '--protocol' in command:
        index = command.index('--protocol')
        del command[index:index + 2]
    command[1:1] = ['--protocol', 'http2']
    service = {
        'image': current['Image'],
        'container_name': 'inxs-cloudflared',
        'entrypoint': config['Entrypoint'],
        'command': command,
        'environment': config['Env'],
        'restart': host['RestartPolicy']['Name'],
        'logging': {'driver': host['LogConfig']['Type'], 'options': host['LogConfig']['Config']},
        'volumes': [],
        'networks': {},
        'labels': {k: v for k, v in config.get('Labels', {}).items() if k.startswith('org.hermes.')},
    }
    service['labels']['org.inxs.release.revision'] = revision
    for source, target in [('Memory', 'mem_limit'), ('MemorySwap', 'memswap_limit'), ('NanoCpus', 'cpus')]:
        if host.get(source):
            service[target] = host[source] / 1e9 if source == 'NanoCpus' else host[source]
    volumes = {}
    for mount in current['Mounts']:
        source = mount.get('Name', mount['Source'])
        service['volumes'].append(source + ':' + mount['Destination'] + (':ro' if not mount['RW'] else ''))
        if mount['Type'] == 'volume':
            volumes[source] = {'external': True}
    networks = {}
    for index, (name, settings) in enumerate(current['NetworkSettings']['Networks'].items()):
        key = 'live' + str(index)
        service['networks'][key] = {'aliases': [a for a in settings.get('Aliases', []) if a != current['Id'][:12]]}
        networks[key] = {'external': True, 'name': name}
    return {'services': {'cloudflared': service}, 'networks': networks, 'volumes': volumes}


if __name__ == '__main__':
    json.dump(release(json.load(sys.stdin), sys.argv[1]), sys.stdout, indent=2)
