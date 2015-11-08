import os

import git

class Project(object):
    def __init__(self):
        self._repo = git.Repo(os.path.dirname(__file__),
                              search_parent_directories=True)

    @property
    def build_dir(self):
        return os.path.join(self._repo.working_dir, 'build')

    @property
    def images_dir(self):
        return os.path.join(self._repo.working_dir, 'images')

    @property
    def services_dir(self):
        return os.path.join(self._repo.working_dir, 'services')

    @property
    def thrift_dir(self):
        return os.path.join(self._repo.working_dir, 'thrift')

project = Project()
