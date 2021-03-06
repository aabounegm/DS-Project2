"""Blueprint creation module. Allows specifying the name and the URL prefix.

To register a blueprint, add it to the `all_blueprints` tuple.
"""

from flask import Blueprint


def _factory(partial_module_string, url_prefix='/'):
    """Generates blueprint objects for view modules.
    Positional arguments:
    partial_module_string -- string representing a view module without
        the absolute path (e.g. 'home.index' for pypi_portal.views.home.index).
    url_prefix -- URL prefix passed to the blueprint.
    Returns:
    Blueprint instance for a view module.
    """
    name = partial_module_string
    import_name = 'src.views'
    blueprint = Blueprint(name, import_name, url_prefix=url_prefix)
    return blueprint


app = _factory('app')
all_blueprints = (app,)
