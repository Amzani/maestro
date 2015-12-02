import subprocess

import yaml

from .graph import Image
from .graph import Service


class Compose(object):
    def __init__(self, compose_mapping):
        self._mapping = compose_mapping

    def export(self):
        """Write the docker-compose.yml file in the current directory
        """
        with open('docker-compose.yml', 'w') as f:
            data = yaml.dump(self._mapping, default_flow_style=False)
            f.write(data)

    def kill(self, *args):
        cmd = ['docker-compose', 'kill']

        if len(args) > 0:
            cmd += args
        call = subprocess.run(cmd)
        return call.returncode == 0

    def run(self, service):
        """Run the 'docker-compose run <service>' command after
        making sure the docker-compose.yml file is exported.
        """
        self.export()

        print('>>> Running service \'{}\' and it\'s dependencies'.format(service))

        cmd = ('docker-compose', 'up', '--no-recreate', service)
        call = subprocess.run(cmd)

        print('>>> Killing service \'{}\' and it\'s dependencies'.format(service))

        # CLeanup after ourselves
        self.kill()

        return call.returncode == 0

    @classmethod
    def from_graph(cls, graph):
        mapping = {}

        def visitor(node):
            if node.hidden:
                return

            if isinstance(node, Image):
                mapping[node.name] = {
                    'image': node.name,
                }
                return

            mapping[node.name] = {
                'image': 'maestro-s-' + node.name,
            }

            links = [
                dep.name
                for dep in graph.neighbors(node) \
                if not dep.hidden
            ]
            if len(links) > 0:
                mapping[node.name]['links'] = links

        graph.visit_dfs(visitor)
        return Compose(mapping)
