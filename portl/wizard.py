import colander
import os

from deform import Form
from deform import ValidationFailure
from deform.widget import CheckedPasswordWidget

from pyramid.httpexceptions import HTTPFound
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
            return SetPasswordForm(self)
        elif self.state == self.ENCRYPTING_DISK:
            return EncryptingDiskForm(self)
        elif self.state == self.SHOW_WIFI_PASSWORD:
            return ShowWifiPasswordForm(self)


class WizardForm(object):
    __parent__ = None
    __name__ = None

    def __init__(self, state):
        super(WizardForm, self).__init__()
        self.state = state


class SetPasswordForm(WizardForm, colander.MappingSchema):
    passphrase = colander.SchemaNode(
        colander.String(), widget=CheckedPasswordWidget(), title='')


class EncryptingDiskForm(WizardForm):
    pass


class ShowWifiPasswordForm(WizardForm):
    pass


@view_config(context=SetPasswordForm,
             renderer='templates/wizard_set_password.pt')
def set_password(context, request):
    form = Form(context, buttons=('next',))
    if 'next' in request.params:
        try:
            data = form.validate(request.params.items())
            passphrase = data['passphrase']
            encrypt_disk(passphrase)
            context.state.state = WizardState.ENCRYPTING_DISK
            context.state.save()
            return HTTPFound(request.url)
        except ValidationFailure, e:
            form = e
    return {'form': form}


def encrypt_disk(passphrase):
    """
    I don't know how to do that.
    """
    pass


@view_config(context=EncryptingDiskForm,
             renderer='templates/wizard_encrypting_disk.pt')
def encrypting_disk(context, request):
    context.state.state = WizardState.SHOW_WIFI_PASSWORD
    context.state.save()
    return {}

@view_config(context=ShowWifiPasswordForm,
             renderer='templates/wizard_show_wifi_password.pt')
def show_wifi_password(context, request):
    context.state.state = WizardState.FINISHED
    context.state.save()
    return {
        'essid': 'TETHR',
        'password': 'abcd1234'
    }
