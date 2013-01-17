from pyramid_layout.layout import layout_config

from .wizard import WizardForm


class Layout(object):
    page_title = 'Tethr'

    def __init__(self, context, request):
        self.context = context
        self.request = request

    def static(self, path):
        return self.request.static_url('portl:static/' + path)

    def deform(self, path):
        return self.request.static_url('deform_bootstrap:static/' + path)


@layout_config(context=WizardForm, template='templates/wizard_layout.pt')
class WizardLayout(Layout):
    page_title = 'Tethr Setup Wizard'
