from contextlib import suppress
import copy
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

    def extend(self, service, config, copy_of=None):
        if copy_of is not None:
            self._mapping[service] = copy.deepcopy(self._mapping[copy_of])
            self._mapping[service]['links']  = [copy_of]

        self._mapping[service].update(config)

    def kill(self, *args):
        subprocess.run(['docker-compose', 'kill'] + list(args))
        subprocess.run(('docker-compose', 'rm', '-f'))

    def run(self, service):
        """Run the 'docker-compose run <service>' command after
        making sure the docker-compose.yml file is exported.
        """
        self.export()

        print('>>> Running service \'{}\' and it\'s dependencies'.format(service))

        call = None
        with suppress(KeyboardInterrupt):
            cmd = ('docker-compose', 'up', '--no-recreate', service)
            call = subprocess.Popen(cmd)
            call.wait()
        call.wait() # This time, ctrl-c will really kill us

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
