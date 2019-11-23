import inspect


def whoami():
    return inspect.stack()[1][3]