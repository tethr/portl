import os
from pyramid.config import Configurator

from .admin import UIRoot
from .wizard import WizardState


def main(global_config, **config):
    settings = global_config.copy()
    settings.update(config)

    var = settings.get('var')
    if not var:
        raise ValueError("'var' must be configured")
    if not os.path.exists(var):
        os.makedirs(var)

    config = Configurator(settings=settings, root_factory=find_root)
    config.include('pyramid_layout')
    config.include('deform_bootstrap')
    config.add_static_view('static', 'portl:static')
    config.add_static_view('deform', 'deform:static')
    config.scan()
    return config.make_wsgi_app()


def find_root(request):
    settings = request.registry.settings
    state = WizardState(settings)
    root = state.find_root()
    if root:
        return root
    return UIRoot(settings)
