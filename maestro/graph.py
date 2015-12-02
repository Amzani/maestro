import os
import subprocess
import sys
import yaml

from enum import Enum

import networkx as nx

from . import docker
from . import fsutils
from . import project
from .config import ServiceConfig


class InvalidServiceError(ValueError):
    """Raised when a service is invalid.

    This can be either the service is not found or missing a properly
    formatted description file.
    """


class DependencyGraph(object):
    """A directed acyclic graph representing the nodes and all it's
    dependencies.
    """
    def __init__(self):
        self._g = nx.DiGraph()
        self.root = None

    def _add_root_node(self, node):
        self._g.add_node(node)
        self.root = node
        return self

    def _freeze(self):
        self._g = nx.freeze(self._g)
        return self

    def neighbors(self, n):
        return self._g.neighbors_iter(n)

    def visit_dfs(self, f):
        for node in nx.dfs_postorder_nodes(self._g, self.root):
            if f(node):
                return

    @classmethod
    def for_image(cls, image_name, hidden=False):
        image = Image.from_name(image_name, hidden)

        dg = DependencyGraph()
        dg._add_root_node(image)

        image._state = NodeState.black
        return dg._freeze()

    @classmethod
    def for_service(cls, service_name):
        service = Service.from_name(service_name)
        if service._state == NodeState.gray:
            raise InvalidServiceError('Dependency cycle detected')
        service._state = NodeState.gray

        dg = DependencyGraph()
        dg._add_root_node(service)

        for dep in service.dependencies:
            if '_build' in dep:
                sub_dg = cls.for_image(dep['_build'], True)
            elif 'image' in dep:
                sub_dg = cls.for_image(dep['image'])
            elif 'service' in dep:
                sub_dg = cls.for_service(dep['service'])
            else:
                assert False, 'Unhandled dependency type {}'.format(next(iter(dep.keys())))

            dg._g = nx.compose(dg._g, sub_dg._g)
            dg._g.add_edge(service, sub_dg.root)

        service._state = NodeState.black
        return dg._freeze()


class NodeState(Enum):
    white = 0
    gray = 1
    black = 2


class Node(object):
    """An abstract element of the dependency graph.
    """
    def __init__(self, name, hidden=False):
        self.name = name
        self.hidden = hidden
        self._state = NodeState.white

    def __str__(self):
        return '[{}] {}'.format(self.__class__.__name__, self.name)

    def build(self):
        raise NotImplemented


_images = {}
class Image(Node):
    def build(self, verbose=False):
        print('>>> Building image \'{}\''.format(self.name))

        image_dir = os.path.join(project.images_dir, self.name)
        if not os.path.isdir(image_dir):
            msg = 'Unknown image \'{}\'. Assuming it already exists.'.format(self.name)
            print(msg, file=sys.stderr)
            return

        fsutils.clone(image_dir, '.')
        return docker.build('.', self.name, verbose=verbose)

    @classmethod
    def from_name(cls, name, hidden=False):
        if name not in _images:
            _images[name] = Image(name, hidden)
        return _images[name]


_services = {}
class Service(Node):
    def __init__(self, name):
        super().__init__(name)
        config_file = os.path.join(self.path, 'maestro.yml')
        self._config = ServiceConfig(config_file, name)

    @property
    def path(self):
        return os.path.join(project.services_dir, self.name)

    @property
    def dependencies(self):
        return self._config.dependencies

    def build(self, verbose=False):
        print('>>> Building service \'{}\''.format(self.name))

        fsutils.clone(self.path, '.')
        return docker.build('.', 'maestro-s-' + self.name, verbose=verbose)

    @classmethod
    def from_name(cls, name):
        if name not in _services:
            _services[name] = Service(name)
        return _services[name]
