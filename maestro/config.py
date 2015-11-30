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
    }

    REQUIRED = ('name', 'type')

    def __init__(self, path, name):
        self._path = path
        self._name = name

        self.update(self.DEFAULTS)

        self.load()
        self.validate()

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
        print(self)

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
        if self.name != self._name:
            msg = 'Names do not match. Expecting \'{}\', got \'{}\''.format(
                self.name, self._name)
            raise InvalidConfig(self._path, msg)
