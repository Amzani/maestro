import argparse
import textwrap

import maestro


parser = argparse.ArgumentParser(
    prog='maestro',
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=maestro.__doc__,
    epilog=textwrap.dedent('''\
        examples:
            maestro image build my-image
            maestro service build my-service-foo
            maestro service test my-service-foo
        '''))


# Positional arguments
positional  = parser.add_argument_group(
    title='Positional arguments',
    description=textwrap.dedent('''\
        These arguments come after any flags and in the order they are
        listed here.
    '''))

positional.add_argument(
    'builder', type=str,
    choices=['image', 'service'],
    help='type of builder')

positional.add_argument(
    'action', type=str,
    help='action the builder must perform')

positional.add_argument(
    'target', type=str,
    help='target on which the builder must perform the action')


# Optional argument

parser.add_argument(
    '-v', '--verbosity', action='count', default=0,
    help='increase output verbosity')
