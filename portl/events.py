from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)

import gobject
import json
import urllib2

from .network import NetworkStatus


def main():
    from NetworkManager import NetworkManager as netman
    loop = gobject.MainLoop()
    for device in netman.GetDevices():
        device.connect_to_signal('StateChanged', update_network)
    loop.run()


def update_network(*args):
    status = NetworkStatus()
    print status
    # FIXME: Don't hardcode URL
    url = 'http://localhost:6543/notify_network_event'
    data = json.dumps(status.as_json())
    urllib2.urlopen(url, data)
