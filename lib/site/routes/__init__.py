
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


'''

Notices
- View notices [edit if owner or has permission]
  * Timeline       <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bulma-timeline@3.0.0/dist/css/bulma-timeline.min.css">
- Approve notices
- Submit notice
  * Calendar       http://creativebulma.net//product/calendar/demo


Bulletin
- View bulletin
- Generate bulletin (HTML and PDF)
# Financing

Sermon outline


Audit Log
'''