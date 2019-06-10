# XXX importing this file has side effects. Namely, it overrides MongoEngine's
# original QuerySet._collection property method.

from flask import g, has_request_context
from mongoengine.queryset.queryset import QuerySet

orig_collection_prop = QuerySet._collection.fget


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


def _patched_collection_prop(self):
    collection = orig_collection_prop(self)
    read_preference = _get_read_preference()
    if read_preference is None:
        return collection
    else:
        return collection.with_options(read_preference=read_preference)

QuerySet._collection = property(_patched_collection_prop)


class read_preference(object):
    def __init__(self, read_preference):
        self.read_preference = read_preference

    def __enter__(self):
        _set_read_preference(self.read_preference)

    def __exit__(self, t, value, traceback):
        _set_read_preference(None)
