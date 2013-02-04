import dbus
from dbus.mainloop.glib import DBusGMainLoop
import gobject

DBusGMainLoop(set_as_default=True)


if __name__ == '__main__':
    from NetworkManager import const
    from NetworkManager import NetworkManager as netman
    loop = gobject.MainLoop()
    for device in netman.GetDevices():
        def callback(new_state, old_state, reason):
            print device.Interface, (
                const('device_state', new_state),
                const('device_state', old_state),
                const('device_state_reason', reason))
        device.connect_to_signal('StateChanged', callback)
    loop.run()
