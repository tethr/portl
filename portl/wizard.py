import colander
import os

from deform import Form
from deform.widget import CheckedPasswordWidget

from pyramid.view import view_config

# Yes, I know this is kind of weird.

class WizardState(object):
    SET_PASSWORD = 'SET PASSWORD'
    ENCRYPTING_DISK = 'ENCRYPTING DISK'
    SHOW_WIFI_PASSWORD = 'SHOW WIFI PASSWORD'
    FINISHED = 'FINISHED'

    def __init__(self, settings):
        self.path = os.path.join(settings['var'], 'wizard_state')
        if os.path.exists(self.path):
            self.load()
        else:
            self.state = self.SET_PASSWORD

    def load(self):
        self.state = open(self.path).read().strip()

    def save(self):
        open(self.path, 'w').write(self.state + '\n')

    def find_root(self):
        if self.state == self.SET_PASSWORD:
            return SetPasswordForm()



class WizardForm(object):
    __parent__ = None
    __name__ = None


class SetPasswordForm(WizardForm, colander.MappingSchema):
    passphrase = colander.SchemaNode(
        colander.String(), widget=CheckedPasswordWidget(), title='')


class EncryptingDiskForm(WizardForm):
    pass


class ShowWifiPasswordForm(WizardForm):
    pass


@view_config(context=SetPasswordForm, renderer='templates/wizard_form.pt')
def set_password(context, request):
    return {'form': Form(context, title='WTF', buttons=('next',))}

