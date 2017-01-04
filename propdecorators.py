"""
These are the various decorators that are applied to the properties of
builder classes. For Details about their function look at the documentation of 
BaseGenericBuilder (and MetaGenericBuilder)
"""

__author__ = 'Arjun Rao'

from .tools import get_builder_type

class frozen_when_frozen:
    """
    Decorator class: When applied to a property setting function of BaseRateGenerator,
    this enforces that the property is not modified if the Rate generator is forces.
    this is automatically applied to all properties of the generat
    """

    def __init__(self, propertyname):
        if not isinstance(propertyname, str):
            raise ValueError("Argument pased to frozenproperty decorator must be of type 'str'")
        else:
            self._propertyname = propertyname

    def __call__(self, func):
        if ('_do_not_freeze' in dir(func) and func._do_not_freeze):
            return func
        else:
            def wrap(s, *args, **kwargs):
                if not s._is_frozen:
                    retval = func(s, *args, **kwargs)
                else:
                    raise(ValueError("Frozen {} builder cannot modify '{}'".format(get_builder_type(s),
                                                                                   self._propertyname)))
                return retval
            
            wrap.__dict__ = func.__dict__.copy()
            wrap.__doc__ = func.__doc__
            return wrap

class cached:

    def __init__(self, cache_entry_name):
        if not isinstance(cache_entry_name, str):
            raise ValueError("Argument pased to frozenproperty decorator must be of type 'str'")
        else:
            self._cache_entry_name = cache_entry_name

    def __call__(self, func):
        if func.__dict__.get('requires_preprocessed'):
            raise Warning(
                'Any function that is `cached` decorated should not already be'
                ' decorated by `requires_preprocessed` as the requires_preprocessed'
                ' decorator is added by the `cached` decorator itself')
        else:
            def wrap(s, *args, **kwargs):
                curr_entry = s._cache.get(self._cache_entry_name)
                if curr_entry:
                    return curr_entry
                else:
                    s._cache[self._cache_entry_name] = func(s, *args, **kwargs)
                    return s._cache[self._cache_entry_name]
            wrap.__dict__ = func.__dict__.copy()
            wrap.__doc__ = func.__doc__
            wrap._cached = self._cache_entry_name
            return requires_preprocessed(wrap)

def requires_preprocessing(func):
    if not func.__dict__.get('_requires_preprocessing'):
        def wrap(self, *args, **kwargs):
            func(self, *args, **kwargs)
            self._is_preprocessed = False
            self._is_frozen_copy_valid = False
        wrap.__dict__ = func.__dict__.copy()
        wrap.__doc__ = func.__doc__
        wrap._requires_preprocessing = True
        return wrap
    else:
        return func

def requires_preprocessed(func):
    if not func.__dict__.get('_requires_preprocessed'):
        def wrap(self, *args, **kwargs):
            if not self._is_preprocessed:
                self.preprocess()
            return func(self, *args, **kwargs)
        wrap.__dict__ = func.__dict__.copy()
        wrap.__doc__ = func.__doc__
        wrap._requires_preprocessed = True
        return wrap
    else:
        return func

def requires_rebuild(func):

    if not func.__dict__.get('_requires_rebuild'):
        def wrap(self, *args, **kwargs):
            func(self, *args, **kwargs)
            self._is_built = False
            self._is_frozen_copy_valid = False
        wrap.__dict__ = func.__dict__.copy()
        wrap.__doc__ = func.__doc__
        wrap._requires_rebuild = True
        return wrap
    else:
        return func

def requires_built(func):

    if not func.__dict__.get('_requires_built'):
        def wrap(self, *args, **kwargs):
            if self._is_built:
                return func(self, *args, **kwargs)
            else:
                raise ValueError("The builder has not been built for the current parameter"
                                 " configuration. This function/property cannot be accessed"
                                 " for an ungenerated array. Run build() to build array")
        wrap.__dict__ = func.__dict__.copy()
        wrap.__doc__ = func.__doc__
        wrap._requires_built = True
        return wrap
    else:
        return func

def do_not_freeze(func):
    func._do_not_freeze = True
    return func