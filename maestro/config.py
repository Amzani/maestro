import yaml


class InvalidConfig(ValueError):
    """Raised when a configuration is invalid.
    """
    def __init__(self, path, msg):
        super().__init__(
            'Invalid configuration file \'{}\': \'{}\''.format(path, msg))


class ServiceConfig(dict):
    DEFAULTS = {
        'dependencies': [],
        'run': {},
    }

    REQUIRED = ('name', 'type')

    def __init__(self, path, name):
        self._path = path
        self._name = name

        self.update(self.DEFAULTS)

        self.load()
        self.validate()

        # Add the image of the services type as a dependency
        self.dependencies.append({
            '_build': 'maestro-base-' + self.type
        })

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError(item)

    def load(self):
        try:
            with open(self._path) as f:
                self.update(yaml.load(f))
        except yaml.YAMLError as e:
            raise InvalidConfig(self._path, str(s))

    def validate(self):
        # Check for missing fields
        missing_fields = set(self.REQUIRED).difference(self.keys())
        if len(missing_fields) > 0:
            msg = 'Missing field{}: {}'.format(
                '' if len(missing_fields) == 1 else 's',
                ', '.join(missing_fields))
            raise InvalidConfig(self._path, msg)

        # Call validate_<key_name> if the method exit
        for key in self.keys():
            fn_name = 'validate_' + key
            if hasattr(self, fn_name) and callable(getattr(self, fn_name)):
                getattr(self, fn_name)()

    def validate_name(self):
        if not isinstance(self.type, str):
            msg = 'Missing string value for \'name\' field.'
            raise InvalidConfig(self._path, msg)

        if self.name != self._name:
            msg = 'Names do not match. Expecting \'{}\', got \'{}\''.format(
                self.name, self._name)
            raise InvalidConfig(self._path, msg)

    def validate_type(self):
        if not isinstance(self.type, str):
            msg = 'Missing string value for \'type\' field.'
            raise InvalidConfig(self._path, msg)

    def validate_dependencies(self):
        if not isinstance(self.dependencies, list):
            msg = 'Missing list value for \'dependencies\' field.'
            raise InvalidConfig(self._path, msg)

        for dep in self.dependencies:
            if not isinstance(dep, dict):
                fmt = 'Invalid dependency \'{}\': not an association.'
                raise InvalidConfig(self._path, fmt.format(dep))
            if len(dep.keys()) != 1:
                fmt = 'Invalid dependency \'{}\': more than one association.'
                raise InvalidConfig(self._path, fmt.format(dep))

            dep_type, name = next(iter(dep.items()))
            if dep_type not in ('image', 'service'):
                fmt = 'Invalid dependency \'{}\': not a \'service\' or \'image\'.'
                raise InvalidConfig(self._path, fmt.format(dep))
            if not isinstance(name, str):
                fmt = 'Invalid dependency \'{}\': Missing string value for a dependency field.'
                raise InvalidConfig(self._path, fmt.format(dep))

    def validate_run(self):
        if not isinstance(self.run, dict):
            msg = 'Missing dict value for \'run\' field.'
            raise InvalidConfig(self._path, msg)
