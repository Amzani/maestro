import sys

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

        self._actions[action](self, target)

    @classmethod
    def from_name(cls, name):
        """Returns the Builder instance for the given builder name"""
        return {
            'image': ImageBuilder,
            'service': ServiceBuilder,
        }[name]()

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
        print('ImageBuilder: {}'.format(target))

class ServiceBuilder(Builder):
    @action
    def build(self, target):
        print('ServiceBuilder: {}'.format(target))

    @action
    def test(self, target):
        print('ServiceBuilder: {}'.format(target))
