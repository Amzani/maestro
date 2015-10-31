import os
import shutil

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

def clone(src, dst):
    """Recursively copy the files and directories of the src dir into dst.
    Note that symlinks are ignored.
    """
    names = os.listdir(src)

    if not os.path.exists(dst):
        os.makedirs(dst)
    elif not os.path.isdir(dst):
        raise ValueError('\'dst\' is not a directory')

    for name in names:
        srcname = os.path.join(src, name)
        dstname = os.path.join(dst, name)

        if os.path.isdir(srcname):
            clone(srcname, dstname)
        elif os.path.isfile(srcname) and not os.path.islink(srcname):
            shutil.copy2(srcname, dstname)
