#!/usr/bin/env python

import argparse
import textwrap

from builders import Builder

def parse_args():
    parser = argparse.ArgumentParser(
        prog='maestro',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description='The best SOA build tool.',
        epilog=textwrap.dedent('''\
        examples:
            maestro image build my-image
            maestro service build my-service-foo
            maestro service test my-service-foo
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
