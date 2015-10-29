import os

from contextlib import contextmanager

@contextmanager
def pushd(path=os.getenv('HOME', None), create=True):
    """Context manager that temporarily changes the working directory
    to path.
    """
    if path is None:
        raise ValueError('path')

    old_path = os.getcwd()

    if not os.path.exists(path):
        os.makedirs(path)
    os.chdir(path)
    yield
    os.chdir(old_path)
