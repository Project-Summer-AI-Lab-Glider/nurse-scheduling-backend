class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls.__name__ not in cls._instances:
            cls._instances[cls.__name__] = super(
                Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls.__name__]
