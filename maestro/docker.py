import subprocess


def build(path, name, verbose=False):
    """Run the 'docker build -t <name> <path>' command.

    Output will be printed to stdout only if verbose is True or the
    command returned a non 0 status code.

    Returns a boolean set to True if the command failed, False
    otherwise.
    """
    cmd = ('docker', 'build', '-t', name, path)

    stdout = None if verbose else subprocess.PIPE
    call = subprocess.run(cmd, stdout=stdout)

    if call.returncode == 0:
        return False

    print(call.stdout.decode('utf-8'))
    return True
