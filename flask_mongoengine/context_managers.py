from flask import g, has_request_context
from mongoengine.queryset.queryset import QuerySet

orig_cursor_args = QuerySet._cursor_args.fget

# In case we're not in a request context
class local_cache(object):
    read_preference = None
cache = local_cache()

def _get_read_preference():
    if has_request_context():
        return getattr(g, 'read_preference', None)
    else:
        return cache.read_preference

def _set_read_preference(val):
    if has_request_context():
        g.read_preference = val
    else:
        cache.read_preference = val


def _patched_cursor_args(self):
    cursor_args = orig_cursor_args(self)
    read_preference = _get_read_preference()
    if read_preference is not None:
        if not 'read_preference' in cursor_args:
            cursor_args['read_preference'] = read_preference
            del cursor_args['slave_okay']
    return cursor_args

QuerySet._cursor_args = property(_patched_cursor_args)

class read_preference(object):
    def __init__(self, read_preference):
        self.read_preference = read_preference

    def __enter__(self):
        _set_read_preference(self.read_preference)

    def __exit__(self, t, value, traceback):
        _set_read_preference(None)
