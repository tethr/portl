from pyramid.i18n import get_localizer
from pyramid.i18n import TranslationStringFactory

import NetworkManager as NETMAN
from NetworkManager import NetworkManager as netman

const = NETMAN.const
_ = TranslationStringFactory('portl')


class NetworkStatus(list):

    def __init__(self):
        super(NetworkStatus, self).__init__()
        for device in netman.GetDevices():
            self.append(make_device(device))

    def as_json(self):
        return [device.as_json() for device in self]


def make_device(device):
    t = device.DeviceType
    if t == NETMAN.NM_DEVICE_TYPE_ETHERNET:
        return EthernetDevice(device)
    elif t == NETMAN.NM_DEVICE_TYPE_WIFI:
        return WifiDevice(device)
    else:
        return UnknownDevice(device)


class Device(object):

    def __init__(self, device):
        self.name = str(device.Interface)
        self.ipv4 = ip4(device.Ip4Address)
        self.ipv6 = ip6(device.Ip6Config)
        self.state = device.State

        self.wifi = self.type == 'wifi'
        self.type = self.type  # Move to instance for sake of __json__

    def __str__(self):
        return '\n'.join([self.type] + [
            '\t%s=%s' % attr for attr in self.__dict__.items()])

    def as_json(self):
        return dict([(k, v) for k, v in self.__dict__.items()
                if not k.startswith('_')])


class EthernetDevice(Device):
    type = 'ethernet'


class WifiDevice(Device):
    type = 'wifi'

    def __init__(self, device):
        super(WifiDevice, self).__init__(device)
        device = device.SpecificDevice()
        self.bitrate = device.Bitrate
        self._ap = device.ActiveAccessPoint
        if hasattr(self._ap, 'Ssid'):
            self.ssid = ''.join([chr(b) for b in self._ap.Ssid])
        else:
            self.ssid = None


class UnknownDevice(Device):
    type = 'unknown'


def ip4(addr):
    """
    Take an integer ip4 address and convert to standard dotted bytes string
    format.
    """
    if not addr:
        return None
    parts = []
    for _ in range(4):
        parts.append(addr&0xff)
        addr >>= 8
    return '.'.join(map(str, parts))


def ip6(config):
    if not isinstance(config, NETMAN.IP6Config):
        return None
    addrs = []
    for addr, prefix, gateway in config.Addresses:
        parts = []
        while addr:
            parts.append(addr.pop(0)<<8 | addr.pop(0))
        for start in xrange(len(parts)):
            if parts[start] == 0:
                for end in xrange(start + 1, len(parts)):
                    if parts[end] != 0:
                        break
                parts[start:end] = [None]
                break
        addrs.append(':'.join(['%x' % part if part else '' for part in parts]))
    return addrs


DEVICE_STATES = {
    NETMAN.NM_DEVICE_STATE_UNKNOWN: _('Unknown'),
    NETMAN.NM_DEVICE_STATE_UNMANAGED: _('Unmanaged'),
    NETMAN.NM_DEVICE_STATE_UNAVAILABLE: _('Unavailable'),
    NETMAN.NM_DEVICE_STATE_DISCONNECTED: _('Disconnected'),
    NETMAN.NM_DEVICE_STATE_PREPARE: _('Preparing'),
    NETMAN.NM_DEVICE_STATE_CONFIG: _('Configuring'),
    NETMAN.NM_DEVICE_STATE_NEED_AUTH: _('Authentication required'),
    NETMAN.NM_DEVICE_STATE_IP_CONFIG: _('Configuring address'),
    NETMAN.NM_DEVICE_STATE_IP_CHECK: _('Checking address'),
    NETMAN.NM_DEVICE_STATE_SECONDARIES: _('Secondaries'),
    NETMAN.NM_DEVICE_STATE_ACTIVATED: _('Active'),
    NETMAN.NM_DEVICE_STATE_DEACTIVATING: _('Deactivating'),
    NETMAN.NM_DEVICE_STATE_FAILED: _('Failed')
}

DEVICE_STATE_UNKNOWN = DEVICE_STATES[NETMAN.NM_DEVICE_STATE_UNKNOWN]


def format_network_status(status, request):
    locale = get_localizer(request)
    for device in status:
        state = DEVICE_STATES.get(device['state'], DEVICE_STATE_UNKNOWN)
        device['state'] = locale.translate(state)
    return status


if __name__ == '__main__':
    for device in NetworkStatus():
        print str(device)
