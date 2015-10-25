#!/usr/bin/env python

import argparse
import textwrap
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


def parse_args():
    parser = argparse.ArgumentParser(
        prog='maestro',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='The paperboy build tool.',
        epilog=textwrap.dedent('''\
        examples:
            maestro image build paperboy-service-python
            maestro service build users
            maestro service test social-accounts
        '''))
    parser.add_argument('builder', type=str,
                        choices=['image', 'service'],
                        help='type of builder')
    parser.add_argument('action', type=str,
                        help='action the builder must perform')
    parser.add_argument('target', type=str,
                        help='target on which the builder must perform the action')
    return parser.parse_args()

def main():
    args = parse_args()

    builder = Builder.from_name(args.builder)
    builder.call(args.action, args.target)

if __name__ == '__main__':
    main()
