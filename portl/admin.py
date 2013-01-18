import json
import math
import os
from pyramid.view import view_config

class UIRoot(object):
    """
    Root object.
    """
    def __init__(self, request):
        pass


@view_config(context=UIRoot, renderer='templates/overview.pt')
def overview(context, request):
    data = get_dummy_overview_data(request)
    data['manage_networks_url'] = '#'
    data['power_log_url'] = '#'
    data['manage_sync_url'] = '#'
    if data['wan']['rate']:
        data['wan']['rate'] = format_bps(data['wan']['rate'])
    return data


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


DUMMY_OVERVIEW_DATA = {
    'wifi': {
        'up': True,
        'essid': 'Tethr',
    },
    'wan': {
        'status': 'Good',
        'rate': 1e6  # bits per second
    },
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
