__author__ = 'Arjun Rao'

from .propdecorators import prop_getter, prop_setter
from abc import ABCMeta

class MetaGenericBuilder(ABCMeta):
    """
    Meta-Class for generic builder classes. To see the list of features of a builder
    class, look at the documentation of base class BaseGenericBuilder. This metaclass
    implements the following.
    
    1.  Checks if the `_build` method is implemented by the class
    2.  All functions and property setters marked with requires_rebuild are
        decorated such that they raise an exception if set on a frozen builder
    3.  For each settable property, a function with_<propname> is created that
        sets the property and returns self allowing for literal programming.

    """

    def __new__(class_, name_, bases_, dict_):

        all_properties = {key:val for key, val in dict_.items()
                          if isinstance(val, property)}
        
        # print("for class {} with bases {}: ".format(name_, bases_))
        # print("settable properties:")
        # print('\n'.join([str(x) for x in all_settable_properties]))
        # print("property setting functions")
        # print('\n'.join([str(x) for x in all_property_setter_funcs]))

        # Ensure that for every property setter,
        # 1.  There is a with_.. function
        # 2.  There is a copy_with_... function
        # 3.  Requirement for preprocessing is signalled
        # 4.  Requirement for rebuilding is signalled (except for those functions marked
        #     with doesnt_require_rebuild). Note that this exception is handled by the
        #     decorator
        # 5.  The properties are frozen as needed (see doesnt_require_rebuild)
        # 6.  They are marked as non_const i.e. cannot be run on immutable builders

        for propname, prop in all_properties.items():
            propsetter = prop_setter(prop.fset) if prop.fset is not None else None
            propgetter = prop_getter(prop.fget) if prop.fget is not None else None
            all_properties[propname] = prop.setter(propsetter).getter(propgetter)

        dict_.update(all_properties)
        # print("In Metaclass")

        return super().__new__(class_, name_, bases_, dict_)
