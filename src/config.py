import os

try:
    import tomllib
except ImportError:  # Python < 3.11
    import tomli as tomllib

# jlint.toml wins over pyproject.toml when both sit in the same directory.
CONFIG_FILES = ('jlint.toml', 'pyproject.toml')

# setting name -> (check, description used in error messages)
SETTINGS = {
    'paths': (lambda v: isinstance(v, list) and all(isinstance(i, str) for i in v),
              'a list of strings'),
    'exclude': (lambda v: isinstance(v, list) and all(isinstance(i, str) for i in v),
                'a list of strings'),
    'max-line-length': (lambda v: isinstance(v, int) and not isinstance(v, bool),
                        'a whole number'),
    'strict': (lambda v: isinstance(v, bool), 'true or false'),
}


class ConfigError(Exception):
    pass


def validate(path, settings):
    for key, value in settings.items():
        if key not in SETTINGS:
            allowed = ', '.join(sorted(SETTINGS))
            raise ConfigError(f"{path}: Unknown setting '{key}' (allowed: {allowed})")
        check, description = SETTINGS[key]
        if not check(value):
            raise ConfigError(f"{path}: '{key}' must be {description}")


def read_config(path):
    """Settings from one file, or None for a pyproject.toml without [tool.jlint]."""
    with open(path, 'rb') as f:
        try:
            data = tomllib.load(f)
        except tomllib.TOMLDecodeError as error:
            raise ConfigError(f"{path}: invalid TOML: {error}")
    if os.path.basename(path) == 'pyproject.toml':
        data = data.get('tool', {}).get('jlint')
        if data is None:
            return None
    validate(path, data)
    return data


def find_config(start):
    """Walk up from `start` to the nearest config. Returns (path, settings) or None."""
    directory = os.path.abspath(start)
    while True:
        for name in CONFIG_FILES:
            path = os.path.join(directory, name)
            if os.path.isfile(path):
                settings = read_config(path)
                if settings is not None:
                    return path, settings
        parent = os.path.dirname(directory)
        if parent == directory:
            return None
        directory = parent
