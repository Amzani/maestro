import sys

def action(func):
    func._action = True
    return func


class Builder(object):
    def __init__(self):
        self._actions = {
            name: func
            for name, func in self.__class__.__dict__.items()
            if hasattr(func, '_action')
        }

    def call(self, action, target):
        if action not in self._actions:
            msg = 'Unknown action \'{}\'. Possible actions are: {}'.format(
                action, ', '.join(self._actions.keys()))
            print(msg, file=sys.stderr)
            return

        self._actions[action](self, target)

    @classmethod
    def from_name(cls, name):
        return {
            'image': ImageBuilder,
            'service': ServiceBuilder,
        }[name]()

class ImageBuilder(Builder):
    @action
    def build(self, target):
        print('ImageBuilder: {}'.format(target))

class ServiceBuilder(Builder):
    @action
    def build(self, target):
        print('ServiceBuilder: {}'.format(target))

    @action
    def test(self, target):
        print('ServiceBuilder: {}'.format(target))
