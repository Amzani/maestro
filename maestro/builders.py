import itertools
import os
import shutil
import subprocess
import sys

from . import fsutils
from . import project

from .compose import Compose
from .context import ExecContext
from .graph import DependencyGraph
from .graph import Image


def action(func):
    func._action = True
    return func


class Builder(object):
    """Parent class for each builders.

    Use the call method to call an action on a target.
    """
    def __init__(self, exec_ctx=ExecContext()):
        self.ctx = exec_ctx
        self._actions = {
            name: func
            for name, func in self.__class__.__dict__.items()
            if hasattr(func, '_action')
        }

    def call(self, action, target, args=[]):
        """Call the given action on the given target"""
        if action not in self._actions:
            msg = 'Unknown action \'{}\'. Possible actions are: {}'.format(
                action, ', '.join(self._actions.keys()))
            print(msg, file=sys.stderr)
            return

        build_dir = os.path.join(project.build_dir,
                                 ':'.join((self._name, action, target)))
        shutil.rmtree(build_dir, ignore_errors=True)

        with fsutils.pushd(build_dir):
            self._actions[action](self, target, args)

    @classmethod
    def from_name(cls, name, exec_ctx=ExecContext()):
        """Returns the Builder instance for the given builder name"""
        builder = {
            'image': ImageBuilder,
            'service': ServiceBuilder,
        }[name](exec_ctx)
        builder._name = name
        return builder


class ImageBuilder(Builder):
    """Builder to manage pure Docker images under the
    "<project_root>/image/" directory.
    """
    @action
    def build(self, target, args=[]):
        """Build the Docker image with the given target name.

        The built is done in a fresh directory. The content of the
        image directory is copied in the build directory.
        """
        image = Image.from_name(target)
        image.build(verbose=(self.ctx.verbosity > 0))


class ServiceBuilder(Builder):
    @action
    def build(self, target, args=[]):
        graph = DependencyGraph.for_service(target)
        graph.visit_dfs(lambda n: n.build(verbose=(self.ctx.verbosity > 0)))

    @action
    def run(self, target, args=[]):
        action = args[0] if len(args) > 0 else 'default'

        # We must build first
        Builder.from_name('service').call('build', target)

        graph = DependencyGraph.for_service(target)
        compose = Compose.from_graph(graph)

        action = args[0] if len(args) > 0 else 'default'
        extended_config = graph.root.run_configs.get(action, {})

        # If an argument was given, add a new entry in compose as an
        # extended copy of target. Else, just extend target.
        if action == 'default':
            action = target
            compose.extend(action, extended_config)
        else:
            compose.extend(action, extended_config, copy_of=target)

        compose.export()

        with open('docker-compose.yml', 'r') as f:
            print(f.read())

        compose.run(action)
