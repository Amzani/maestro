import os

import git

_repo = git.Repo(os.path.dirname(__file__),
                 search_parent_directories=True)

build_dir = os.path.join(_repo.working_dir, 'build')
images_dir = os.path.join(_repo.working_dir, 'images')
services_dir = os.path.join(_repo.working_dir, 'services')
thrift_dir = os.path.join(_repo.working_dir, 'thrift')
