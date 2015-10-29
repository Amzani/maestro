import os

import git

class Project(object):
    def __init__(self):
        self._repo = git.Repo(os.path.dirname(__file__),
                              search_parent_directories=True)

    @property
    def build_dir(self):
        return os.path.join(self._repo.working_dir, 'build')

project = Project()
