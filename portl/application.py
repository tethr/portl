from gevent import monkey; monkey.patch_all()

import os
import pkg_resources

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

    config = Configurator(
        settings=settings,
        root_factory=find_root,
        locale_negotiator=locale_negotiator,
    )
    config.include('pyramid_layout')
    config.include('deform_bootstrap')
    config.add_static_view('static', 'portl:static')
    config.add_static_view('deform', 'deform:static')
    config.add_translation_dirs("portl:locale")
    config_client_templates(config)
    config.scan()
    return config.make_wsgi_app()


def config_client_templates(config):
    for fname in pkg_resources.resource_listdir('portl', 'templates/client'):
        if not fname.endswith('.pt'):
            continue
        renderer = 'portl:/templates/client/' + fname
        name = fname[:-3]
        config.add_panel(name=name, renderer=renderer)


def find_root(request):
    settings = request.registry.settings
    state = WizardState(settings)
    root = state.find_root()
    if root:
        return root
    return UIRoot(settings)


DEFAULT_LOCALE = 'en'
AVAILABLE_LOCALES = set(['en', 'it'])

def locale_negotiator(request):
    # Pass accept language header through a cookie to work around Chromium bug
    # http://code.google.com/p/chromium/issues/detail?id=174956
    if not request.accept_language:
        accept = request.cookies.get('accept_language')
        if accept:
            request.accept_language = accept
    request.response.set_cookie('accept_language', str(request.accept_language))

    for locale in request.accept_language:
        if locale in AVAILABLE_LOCALES:
            return locale
    return DEFAULT_LOCALE
