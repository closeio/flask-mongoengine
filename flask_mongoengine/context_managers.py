# XXX importing this file has side effects. Namely, it overrides MongoEngine's
# original QuerySet._collection property method.

import threading

from mongoengine.queryset.queryset import QuerySet

orig_collection_prop = QuerySet._collection.fget

_read_preference = threading.local()
_read_preference.value = None


def _get_read_preference():
    return _read_preference.value


def _set_read_preference(val):
    _read_preference.value = val


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
