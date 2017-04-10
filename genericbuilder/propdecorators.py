"""
These are the various decorators that are applied to the properties of
builder classes. For Details about their function look at the documentation of 
BaseGenericBuilder (and MetaGenericBuilder)
"""

__author__ = 'Arjun Rao'


def prop_getter(func):
    
    if not func.__dict__.get('_prop_getter'):    
        def prop_getter_wrap(self, *args, **kwargs):
            if not self._is_preprocessed:
                self.preprocess()  # will throw exception if immutable
            return func(self, *args, **kwargs)
        prop_getter_wrap.__dict__ = func.__dict__.copy()
        prop_getter_wrap.__doc__ = func.__doc__
        prop_getter_wrap._prop_getter = True
    else:
        prop_getter_wrap = func
    return prop_getter_wrap


def prop_setter(func):
    if not func.__dict__.get('_prop_getter'):    
        def prop_setter_wrap(self, *args, **kwargs):
            if not self._is_mutable:
                raise AttributeError('Properties cannot be set on immutable builders')
            if self._is_frozen:
                raise AttributeError('Properties cannot be set on frozen builders')

            # Since a property will be changed, invalidating the preprocessed and built
            # state
            self._is_built = False
            self._is_preprocessed = False
            return func(self, *args, **kwargs)
        prop_setter_wrap.__dict__ = func.__dict__.copy()
        prop_setter_wrap.__doc__ = func.__doc__
        prop_setter_wrap._prop_setter = True
    else:
        prop_setter_wrap = func
    return prop_setter_wrap


def requires_built(func):
    """
    Apply this to any function that depends on a built state before execution. Note
    that this can be applied to property getters whose values are only defined
    after a build has been done. E.g. in the case of a rate builder, the
    `rate_array` property only has a valid value after `build()` is called.

    NOTE: When using this, one needn't use the @prop_getter decorator on the function
    """
    if func.__dict__.get('_requires_built') is None:
        def wrap(self, *args, **kwargs):
            if self._is_built:
                return func(self, *args, **kwargs)
            else:
                raise ValueError("The builder has not been built for the current parameter"
                                 " configuration. This function/property cannot be accessed"
                                 " for an unbuilt builder. Run build() before accessing said"
                                 " property")
        wrap.__dict__ = func.__dict__.copy()
        wrap.__doc__ = func.__doc__
        wrap._requires_built = True
        return wrap
    else:
        return func
