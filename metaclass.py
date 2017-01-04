__author__ = 'Arjun Rao'

from .propdecorators import frozen_when_frozen

class MetaGenericBuilder(type):
    """
    Meta-Class for generic builder classes. To see the list of features of a builder
    class, look at the documentation of base class BaseGenericBuilder. This metaclass
    implements the following.
    
    1.  Checks if the `_build` method is implemented by the class
    2.  All property setters not explicitly marked with the @do_not_freeze decorator
        are decorated such that they raise an exception if set on a frozen builder
    3.  For each settable property, a function with_<propname> is created that sets
        the property and returns self allowing for literal programming.

    """

    def __new__(class_, name_, bases_, dict_):

        has_build = '_build' in dict_
        
        if not has_build:
            raise ValueError("A builder class must implement the _build() method"
                             " building whatever")

        all_settable_properties = [(key, val) for key, val in dict_.items()
                                   if isinstance(val, property) and val.fset is not None]
        print("for class {} with bases {}: ".format(name_, bases_))
        print("settable properties:")
        print('\n'.join([str(x) for x in all_settable_properties]))

        # Freezing all settable properties
        for propname, prop in all_settable_properties:
            dict_[propname] = property(
                fget=prop.fget,
                fset=frozen_when_frozen(propname)(prop.fset),
                doc=prop.__doc__)

        # creating get and set property functions
        all_properties = [(key, val) for key, val in dict_.items() if isinstance(val, property)]
        def get_properties(self):

            if bases_:
                prop_dict = bases_[0].get_properties(self)
            else:
                prop_dict = {}

            for propname, propvalue in all_properties:
                prop_dict[propname] = propvalue.__get__(self)

            return prop_dict
        dict_['get_properties'] = get_properties

        all_settable_properties = [(key, val) for key, val in all_properties if val.fset is not None]
        def set_properties(self, prop_dict):
            # unlike get, this does not call the base class setter
            # in case of overridden setters. the pop ensures that
            for propname, propvalue in all_settable_properties:
                if propname in prop_dict:
                    propvalue.__set__(self, prop_dict.pop(propname))
            if bases_:
                 bases_[0].set_properties(self, prop_dict)
        dict_['set_properties'] = set_properties

        def get_literal_programming_setter(propertyname):
            def set_property_and_return_func(self, propvalue):
                self.__setattr__(propertyname, propvalue)
                return self
            return set_property_and_return_func
        
        # Adding with_property functions for literal programming
        for propname, prop in all_settable_properties:
            dict_["with_{}".format(propname)] = get_literal_programming_setter(propname)

        print("In Metaclass")

        return super().__new__(class_, name_, bases_, dict_)