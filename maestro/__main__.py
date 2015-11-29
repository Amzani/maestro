#!/usr/bin/env python
"""Maestro's main entry point. Invoked as 'maestro' or 'python -m
maestro'.
"""
import sys

from .core import main


if __name__ == '__main__':
    sys.exit(main())
