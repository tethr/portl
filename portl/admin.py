import gevent
import gevent.queue
import json
import math
import os
import socketio
import socketio.namespace

from pyramid.response import Response
from pyramid.view import view_config

from .network import NetworkStatus


network_events = gevent.queue.Queue()
status_loop = None


class UIRoot(object):
    """
    Root object.
    """
    def __init__(self, request):
        pass


@view_config(context=UIRoot, renderer='templates/overview.pt')
def overview(context, request):
    layout = request.layout_manager.layout
    layout.use_template('network')
    data = {
        'network_status': NetworkStatus().as_json()
    }
    layout.set_json_data(data)

    data = get_dummy_overview_data(request)
    data['power_log_url'] = '#'
    data['manage_sync_url'] = '#'
    if data['wan']['rate']:
        data['wan']['rate'] = format_bps(data['wan']['rate'])
    if data['battery']['time_left']:
        data['battery']['time_left'] = format_time_left(
            data['battery']['time_left'])
    return data


@view_config(context=UIRoot, name="socket.io")
def status_io(request):
    start_status_loop(request)
    socketio.socketio_manage(
        request.environ, {'/status': socketio.namespace.BaseNamespace},
        request=request)
    return Response('')


@view_config(context=UIRoot, name="notify_network_event")
def notify_network_event(request):
    # FIXME make sure request is coming from our local notification daemon
    # and not some hooligans.
    network_events.put(request.json_body)
    return Response('')


def poll_network(server):
    while True:
        status = {'network_status': network_events.get()}
        packet = {
            'type': 'event',
            'name': 'network',
            'args': status,
            'endpoint': '/status'}
        for socket in server.sockets.itervalues():
            socket.send_packet(packet)
        gevent.sleep(0) # theoretically unnecessary


def start_status_loop(request):
    global status_loop
    if status_loop is not None:
        return

    print 'Start loop'
    socket = request.environ['socketio']
    status_loop = gevent.spawn(poll_network, socket.server)


def get_dummy_overview_data(request):
    var = request.registry.settings.get('var')
    path = os.path.join(var, 'dummy_overview.json')
    if not os.path.exists(path):
        json.dump(DUMMY_OVERVIEW_DATA, open(path, 'w'), indent=4)
        return DUMMY_OVERVIEW_DATA
    return json.load(open(path))


def format_bps(bps):
    places = math.log10(bps)
    if places < 3:
        return str(bps) + ' bps'
    elif places < 6:
        return '%0.2f kbps' % (bps/1e3)
    elif places < 9:
        return '%0.2f mbps' % (bps/1e6)
    else:
        return '%0.2f gbps' % (bps/1e9)


def format_time_left(seconds):
    seconds = int(seconds)
    if seconds < 60:
        return str(seconds) + 's'
    minutes = int(seconds / 60)
    seconds = seconds % 60
    if minutes < 60:
        return '%dm %ds' % (minutes, seconds)
    hours = int(minutes / 60)
    minutes = hours % 60
    return '%dh %dm %ds' % (hours, minutes, seconds)


DUMMY_OVERVIEW_DATA = {
    'battery': {
        'charging': True,
        'percent_left': 20,
        'time_left': 3000 # seconds
    },
    'solar': {
        'output': 14,  # Volts
        'sunny': True
    },
    'files': {
        'in_sync': False,
        'in_progress': True,
        'last_sync': '2013-01-18T13:34',
    }
}
