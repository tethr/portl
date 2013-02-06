from dbus.mainloop.glib import DBusGMainLoop
DBusGMainLoop(set_as_default=True)

import gobject
import json
import redis

from .network import NetworkStatus


def main():
    from NetworkManager import NetworkManager as netman
    loop = gobject.MainLoop()
    for device in netman.GetDevices():
        device.connect_to_signal('StateChanged', RedisPublisher())
    loop.run()


class RedisPublisher(object):
    channel = 'tethr.status.network'

    def __init__(self):
        self.redis = redis.StrictRedis()

    def __call__(self, *args):
        status = NetworkStatus()
        data = json.dumps(status.as_json())
        self.redis.publish(self.channel, data)
