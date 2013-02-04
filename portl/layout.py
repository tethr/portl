from pyramid.renderers import render
from pyramid_layout.layout import layout_config
from pyramid_layout.panel import panel_config

from .wizard import WizardForm


@layout_config(template='templates/admin_layout.pt')
class Layout(object):
    page_title = 'Tethr'
    data = None

    def __init__(self, context, request):
        self.context = context
        self.request = request
        self.client_templates = []

    def static(self, path):
        return self.request.static_url('portl:static/' + path)

    def deform(self, path):
        return self.request.static_url('deform:static/' + path)

    def use_template(self, *args):
        self.client_templates.extend(args)

    def set_json_data(self, data):
        self.data = render('json', data)


@layout_config(context=WizardForm, template='templates/wizard_layout.pt')
class WizardLayout(Layout):
    page_title = 'Tethr Setup Wizard'


@panel_config('client-templates')
def client_templates(context, request):
    lm = request.layout_manager
    names = lm.layout.client_templates
    if not names:
        return ''
    panel = []
    for name in names:
        panel.append(
            '<script id="%s" type="text/x-handlebars-template">' % name)
        panel.append(lm.render_panel(name))
        panel.append('</script>')
    return '\n'.join(panel)
