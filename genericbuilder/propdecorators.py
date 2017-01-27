"""
These are the various decorators that are applied to the properties of
builder classes. For Details about their function look at the documentation of 
BaseGenericBuilder (and MetaGenericBuilder)
"""

__author__ = 'Arjun Rao'

from .tools import get_builder_type
import copy as cp

class frozen_when_frozen:
    """
    Decorator class: When applied to a property setting function of BaseRateGenerator,
    this enforces that the property is not modified if the Rate generator is forces.
    this is automatically applied to all properties of the generator. It does not freeze
    any function that is marked with the doesnt_require_rebuild decorator
    """

    def __init__(self, propertyname):
        if not isinstance(propertyname, str):
            raise ValueError("Argument pased to frozenproperty decorator must be of type 'str'")
        else:
            self._propertyname = propertyname

    def __call__(self, func):
        if ('_requires_rebuild' in dir(func) and not func._requires_rebuild):
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

class non_const:
    """
    This decorator is automatically applied to all property setters. It basically
    disallows their use if the object is Immutable
    """

    def __init__(self, propertyname):
        if not isinstance(propertyname, str):
            raise ValueError("Argument pased to frozenproperty decorator must be of type 'str'")
        else:
            self._propertyname = propertyname

    def __call__(self, func):
        def wrap(s, *args, **kwargs):
            if s._is_mutable:
                retval = func(s, *args, **kwargs)
            else:
                raise(ValueError("Immutable {} builder cannot modify '{}'".format(get_builder_type(s),
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


class property_setter:
    """
    This class is used to mark any function as a property setter. This is useful for
    complex property setter functions that cannot be implemented in an assignment
    statement
    """
    def __init__(self, propertyname):
        if not isinstance(propertyname, str):
            raise ValueError("Argument pased to frozenproperty decorator must be of type 'str'")
        else:
            self._propertyname = propertyname

    def __call__(self, func):
        wrap = cp.copy(func)
        wrap._property_setter = self._propertyname
        return wrap


def _requires_preprocessing(func):
    """
    This never needs to be applied directly. Applied to all property setters by default.
    (See cached and property_setter)
    (NEED TO WRITE))
    """
    if not func.__dict__.get('_requires_preprocessing'):
        def wrap(self, *args, **kwargs):
            func(self, *args, **kwargs)
            self._is_preprocessed = False
        wrap.__dict__ = func.__dict__.copy()
        wrap.__doc__ = func.__doc__
        wrap._requires_preprocessing = True
        return wrap
    else:
        return func


def requires_preprocessed(func):
    """
    Apply this to any function that depends on a preprocessed state before execution.
    """
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


def _requires_rebuild(func):
    """
    This never needs to be used directly. This is applied on all properties by default.
    use doesnt_require_rebuild if a property setter doesnt need rebuilding. NOTE: This will
    not overload existing rebuild status and will instead simply do nothing and return the
    function as is
    """

    if func.__dict__.get('_requires_rebuild') is None:
        def wrap(self, *args, **kwargs):
            func(self, *args, **kwargs)
            self._is_built = False
        wrap.__dict__ = func.__dict__.copy()
        wrap.__doc__ = func.__doc__
        wrap._requires_rebuild = True
        return wrap
    else:
        return func


def doesnt_require_rebuild(func):
    """
    This is used to exlicitly declare that a property setter doesn't require rebuilding.
    This will also cause the property setter to not be frozen. Note: Dont use this for
    overriding rebuild status of existing property_setter, this will not do it and will
    simply quit
    """

    if func.__dict__.get('_requires_rebuild') is None:
        wrap = cp.copy(func)
        wrap._requires_rebuild = False
        return wrap
    else:
        return func


def requires_built(func):
    """
    Apply this to any function that depends on a built state before execution.
    """
    if func.__dict__.get('_requires_built') is None:
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
