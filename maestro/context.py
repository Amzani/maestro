class ExecContext(object):
    """All information about the execution context.

    Default attribute values are given, but can be overwritten either
    as keywords arguments given to the constructor or as simple
    assignements.
    """
    verbosity = 0

    def __init__(self, **kwargs):
        assert all(hasattr(type(self), attr) for attr in kwargs.keys())
        self.__dict__.update(**kwargs)
