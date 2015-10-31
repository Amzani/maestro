import os
import shutil
import subprocess
import sys

import fsutils

from project import project

def action(func):
    func._action = True
    return func


class Builder(object):
    """Parent class for each builders.

    Use the call method to call an action on a target.
    """
    def __init__(self):
        self._actions = {
            name: func
            for name, func in self.__class__.__dict__.items()
            if hasattr(func, '_action')
        }

    def call(self, action, target):
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
            self._actions[action](self, target)

        shutil.rmtree(build_dir, ignore_errors=True)

    @classmethod
    def from_name(cls, name):
        """Returns the Builder instance for the given builder name"""
        builder = {
            'image': ImageBuilder,
            'service': ServiceBuilder,
        }[name]()
        builder._name = name
        return builder


class ImageBuilder(Builder):
    """Builder to manage pure Docker images under the
    "<paperboy_root>/image/" directory.
    """
    @action
    def build(self, target):
        """Build the Docker image with the given target name.

        The built is done in a fresh directory. The content of the
        image directory is copied in the build directory, followed by
        the content of the "<paperboy_root>/thrift/" directory.
        """
        image_dir = os.path.join(project.images_dir, target)
        if not os.path.isdir(image_dir):
            print('Unknown image \'{}\'.'.format(target), file=sys.stderr)
            return

        fsutils.clone(image_dir, '.')
        fsutils.clone(project.thrift_dir, '.')
        subprocess.run(('docker', 'build', '-t', target, '.'))

class ServiceBuilder(Builder):
    @action
    def build(self, target):
        print('ServiceBuilder: {}'.format(target))

    @action
    def test(self, target):
        print('ServiceBuilder: {}'.format(target))
