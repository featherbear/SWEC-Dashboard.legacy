
__modules = {}


def __init__():
    import importlib
    import pkgutil

    for _, fp, _ in pkgutil.walk_packages(path=pkgutil.extend_path(__path__, __name__), prefix=__name__ + '.'):
        pyfile = fp[len(__name__) + 1:]
        try:
            __modules[pyfile] = importlib.import_module(fp)
        except Exception as e:
            print("Error importing " + pyfile + " - " + str(e))
    return __modules


__init__()
