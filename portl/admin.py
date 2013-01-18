from pyramid.view import view_config

class UIRoot(object):
    """
    Root object.
    """
    def __init__(self, request):
        pass


@view_config(context=UIRoot, renderer='templates/overview.pt')
def overview(context, request):
    return {}
