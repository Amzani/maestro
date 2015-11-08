import os

import yaml

from project import project


class InvalidServiceError(ValueError):
    """Raised when a service is invalid.

    This can be either the service is not found or missing a properly
    formatted description file.
    """


def _desc_service(name):
    desc_file_path = os.path.join(project.services_dir, name, 'service.yml')

    try:
        with open(desc_file_path) as desc_file:
            desc = yaml.load(desc_file)
    except (FileNotFoundError, yaml.YAMLError) as e:
        raise InvalidServiceError(e)

    # Check that the description is valid
    fields = desc.keys() if desc is not None else set()
    required_fields = set(('name',))
    missing_fields = required_fields.difference(fields)

    if len(missing_fields) > 0:
        msg = 'Missing \'{}\' field{}.'.format(
            ','.join(missing_fields),
            '' if len(missing_fields) == 1 else 's')
        raise InvalidServiceError(msg)

    if desc['name'] != name:
        msg = 'Names do not match (\'{}\' against \'{}\')'.format(
            desc['name'], name)
        raise InvalidServiceError(msg)

    return desc

class Service(object):
    def __init__(self, name):
        self.name = name
        self._desc = _desc_service(name)

    @property
    def dependencies(self):
        return self._desc.get('dependencies', [])
