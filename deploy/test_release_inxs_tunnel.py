import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('tunnel_release', Path(__file__).with_name('release-inxs-tunnel.py'))
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class TunnelReleaseTest(unittest.TestCase):
    def test_only_transport_changes_and_production_boundaries_survive(self):
        live = {'Id': 'a' * 64, 'Image': 'sha256:fixed',
                'Config': {'Cmd': ['tunnel', '--no-autoupdate', 'run', '--token', 'secret'],
                           'Entrypoint': ['cloudflared'], 'Env': ['TUNNEL_TOKEN=secret'],
                           'Labels': {'org.hermes.container-tls.revision': 'tls', 'com.docker.compose.project': 'old'}},
                'HostConfig': {'RestartPolicy': {'Name': 'unless-stopped'}, 'Memory': 128000000,
                               'MemorySwap': 256000000, 'LogConfig': {'Type': 'json-file', 'Config': {'max-size': '10m'}}},
                'Mounts': [{'Type': 'bind', 'Source': '/tls/ca', 'Destination': '/cert', 'RW': False}],
                'NetworkSettings': {'Networks': {'existing': {'Aliases': ['cloudflared']}}}}
        result = module.release([live], 'revision')
        self.assertEqual(list(result['services']), ['cloudflared'])
        service = result['services']['cloudflared']
        self.assertEqual(service['command'], ['tunnel', '--protocol', 'http2', '--no-autoupdate', 'run', '--token', 'secret'])
        self.assertEqual(service['image'], live['Image'])
        self.assertEqual(service['environment'], live['Config']['Env'])
        self.assertEqual(service['mem_limit'], 128000000)
        self.assertEqual(service['volumes'], ['/tls/ca:/cert:ro'])
        self.assertEqual(result['networks']['live0']['name'], 'existing')
        self.assertEqual(service['labels']['org.hermes.container-tls.revision'], 'tls')
        self.assertNotIn('com.docker.compose.project', service['labels'])
        live['Config']['Cmd'] = service['command']
        self.assertEqual(module.release([live], 'revision')['services']['cloudflared']['command'], service['command'])

    def test_unexpected_command_is_rejected(self):
        with self.assertRaises(ValueError):
            module.release([{'Config': {'Cmd': ['unexpected']}, 'HostConfig': {}}], 'revision')


if __name__ == '__main__':
    unittest.main()
