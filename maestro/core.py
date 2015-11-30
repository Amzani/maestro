import argparse
import textwrap

from . import cli
from .builders import Builder
from .context import ExecContext


def main():
    ctx = ExecContext()
    cli.parser.parse_args(namespace=ctx)

    builder = Builder.from_name(ctx.builder, exec_ctx=ctx)
    builder.call(ctx.action, ctx.target)

if __name__ == '__main__':
    main()
