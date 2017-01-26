__author__ = 'Arjun Rao'


from collections import Mapping

def get_builder_type(obj_or_class):
    if 'builder_type' in dir(obj_or_class):
        builder_type = obj_or_class.builder_type
    else:
        builder_type = None
    return builder_type


def get_unsettable(base_class, property_name):
    def no_set_func(self, value):
        if value is None:
            getattr(base_class, 'with_{}'.format(property_name))(self, None)
        else:
            raise AttributeError("Property {} Not Settable".format(property_name))
    return getattr(base_class, property_name).setter(no_set_func)

# This code has been borrowed from http://stackoverflow.com/a/9997519/3140750
class ImmutableDict(Mapping):
    def __init__(self, somedict):
        self._dict = dict(somedict)   # make a copy
        self._hash = None

    def __getitem__(self, key):
        return self._dict[key]

    def __len__(self):
        return len(self._dict)

    def __iter__(self):
        return iter(self._dict)

    def __hash__(self):
        if self._hash is None:
            self._hash = hash(frozenset(self._dict.items()))
        return self._hash
