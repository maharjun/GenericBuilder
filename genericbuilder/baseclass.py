__author__ = 'Arjun Rao'

import copy as cp

from .metaclass import MetaGenericBuilder
from .propdecorators import *


class BaseGenericBuilder(metaclass=MetaGenericBuilder):
    """
        =========================
         Generic Builder Classes
        =========================

        What is a Builder Class
        =======================

        The builder class is a class that satisfies all the following properties

        1.  Inherits from BaseGenericBuilder or some subclass of BaseGenericBuilder.

        2.  Implements the _build() method 'building' whatever needs to be built (e.g.
            rate array, spike array, input current array). The _build() function may
            call the super _build() if one wishes to make use of whatever the super
            class builds.

        3.  All properties must be exposed via getter and setter methods. This confers
            some interesting benifits (see properties of properties section). One may
            also use decorators (see prop-of-prop section) to control the behaviour of
            the class upon setting or getting the parameters.

        3.  (Optionally) Implements the _preprocess() method where any preprocessing
            input parameters are done. (see decorators requires_preprocessed and
            requires_preprocessing, also see the generate() function). The _preprocess()
            function must call the super _preprocess() function.

        4.  NO FUNCTION call will mutate an existing data member. This is essential
            to ensure correctness when performing copy_frozen(). [Note that this is a
            pretty stringent requirement and basically requiresus to do a lot of work
            at one time rather than incrementally change existing properties every
            time a function is called]

        5.  The __init__ function must offer parameter initialization through a dict
            specifying the parameters. It must not return an exception if some of the
            keys in the dict are not supported.

        How Does It Work?
        =================

        Basic Structure
        ***************

        1.  A Builder class that satisfies the above properties is a class that is
            created using the meta-class MetaGenericBuilder.
        
        2.  A builder object can be either mutable or frozen. A frozen builder object
            loses the ability to execute __init__(), build() (note. no underscore) and
            the ability to set any property not explicitly decorated by the `do_not_freeze`
            decorator
        
        3.  A mutable builder object has the following status properties (READ-ONLY)

            a.  `is_preprocessed`
                  This flag represents that all internal variables (except
                  those that are built using _build) are consistent with the externally
                  supplied properties.

            b.  `is_built`
                  This flag represents whether the variables built by _build() are 
                  consistent. Note however tha running the build() function ensures
                  that both `is_built` and `is_preprocessed` are True. Only builder
                  objects that have `is_built` as True can generate a frozen copy via
                  `copy_frozen()`

            These flags are typically affected by the decorated setters and getters of
            properties (Hence requirement 3, see also properties of properties section).
            Note that it is ensured before returning a frozen generator that both of the
            above flags are True.

        4.  See documentation for build() and process() to see what they do

        Parameter Setting and Getting
        *****************************

        1.  The above is typically accomplished via property getters and setters or via
            a dict passed to __init__
        2.  When an object is frozen, only properties with setters explicitly decorated
            as do_not_freeze can be set
        3.  Depending on the decorator assigned to the property, one may need to run build()
            before being able to use the built properties of the object

        Properties of Properties
        ------------------------

        The forced use of properties to export members allows for interesting benefits.
        Before that, we need to look at various decorators that endow special properties
        to the properties
            
        1.  *frozen_when_frozen(propname)*
              This decorator when applied to a setter ensures that the setter is not
              executable if the object is frozen. This does not need to be applied
              explicitly as the Metaclass applies it by default for all property
              setters

        2.  *do_not_freeze*
              Since, by default, all properties are frozen (made unsettable) when
              the builder is frozen. This decorator when applied to the setter of a
              property, ensures that the property is settable even if the builder is
              frozen. **NOTE - ** Any property that is marked with do_not_freeze
              should not mutate any existing data members. This is to ensure that
              the memory sharing implemented by the frozen to frozen copying does not
              result in spurious propagation of changes through the copies

        3.  *requires_preprocessing*
              This decorator when applied to a setter of the property ensures that
              the setting of the property signals the need to perform preprocessing
              when needed
        
        4.  *requires_preprocessed*
              This decorator when applied to the getter of the property signifies that
              preprocessing needs to be done before this property is returned. Thus,
              preprocess() is called if preprocessing is required before returning the
              property
        
        5.  *requires_regeneration*
              This decorator when applied to a setter of the property ensures that
              the setting of the properties signals the need to perform rebuilding
              before whatever is built is consistent with the current properties.
              Typically this applies to properties that have the requires_generated
              decorator

        6.  *requires_generated*
              This decorator when applied to the getter of a property implies that
              the property can only be retrieved if the build is consistent with the
              parameters. Thus if buiding is required (e.g. by setting a property having
              the requires_regeneration flag), and has not been done by a call to build,
              it will return an exception.

        All the above decorators except frozen_type (which is applied by default) can be
        used in any order but must come inside the property decorator. Decorators do_not_freeze,
        requires_regeneration, requires_preprocessing, are typically used on property setters.
        requires_generated, and requires_preprocessed are usually used on getters of derived
        properties. To see usage, see any implementation of the Builder class.

        Preprocessing and Building
        **************************
        The processing of the parameters to perform the building is done in 2 steps:

        <NEED TO WRITE>

        How does Copying Work?
        **********************
        
        copy
        copy_frozen
        copy_mutable

        <NEED TO WRITE>
    """

    builder_type = 'generic'

    _shallow_copied_vars = set()

    def __init__(self, conf_dict=None):
        """Constructor for BaseRateGenerator

        Since this builder builds exactly nothing, thus there are no properties to to set
        or get via any dict
        """
        
        self._is_frozen = False
        self._is_built = False
        self._is_preprocessed = False
        self._is_frozen_copy_valid = False
        self._frozen_copy = False
        self._is_view = False

    def build(self):
        """Performs build"""
        if not self._is_frozen:
            if not self._is_preprocessed:
                self.preprocess()
            self._cache = {}
            self._build()
            self._is_built = True
        else:
            # Do nothing. frozen builder is already in built state
            pass
        return self

    def preprocess(self):
        self._preprocess()
        self._is_preprocessed = True
        # Clear All caches
        self._cache = {}

        return self

    def _build(self):
        pass

    def _preprocess(self):
        pass

    def copy(self):
        """
        Returns a Copy of the Generator
        """
        if self._is_frozen:
            return self.copy_frozen()
        else:
            return self.copy_mutable()

    def copy_frozen(self):
        """
        Returns a frozen copy of the generator. This function performs cached copying as follows
        
        NEED TO WRITE DOCUMENTATION AS TO EXACTY HOW THIS WORKS
        """
        
        self._generate_frozen_copy()
        if self._is_frozen and self._is_view:
            new_obj = self._frozen_copy.copy_frozen()
        elif self._is_frozen:
            new_obj = self._shallow_copy()
            new_obj._is_frozen_copy_valid = False
            new_obj._frozen_copy = None
        elif self._is_built:
            new_obj = self._frozen_copy.copy_frozen()
        else:
            raise AttributeError(
                "A frozen copy cannot be created for a Builder which"
                " has not built consistent to input parameters Make"
                " sure you run build().")

        return new_obj

    def copy_mutable(self):
        """
        Returns a changing (non-frozen) copy of the current generator. Performs deep copy of
        __dict__
        """
        new_obj = self._deep_copy()
        new_obj._is_frozen = False
        return new_obj

    def frozen_view(self):
        """
        Returns a frozen (RO) view of the rate generator. This is not guaranteed to
        remain consistent across calls to functions of the original RateBuilder. If
        that is required, then use one of the copy functions. This function performs
        no reallocation of memory
        """
        new_obj = self._shallow_copy()
        new_obj._is_frozen = True
        new_obj._is_frozen_copy_valid = False
        new_obj._is_view = True
        new_obj._frozen_copy = None
        return new_obj

    def _generate_frozen_copy(self):
        if not self._is_frozen_copy_valid:
            if self._is_frozen and self._is_view:
                self._frozen_copy = self._deep_copy()
                self._frozen_copy._is_frozen_copy_valid = False
                self._frozen_copy._frozen_copy = None
                self._frozen_copy._is_view = False
            elif self._is_frozen:
                pass
            elif self._is_built:
                self._frozen_copy = self._deep_copy()
                self._frozen_copy._is_frozen_copy_valid = False
                self._frozen_copy._frozen_copy = None
                self._frozen_copy._is_frozen = True
            else:
                raise AttributeError(
                    "A frozen copy cannot be created for a Builder which"
                    " has not built consistent to input parameters Make"
                    " sure you run build().")
            
            self._is_frozen_copy_valid = True

    def _deep_copy(self, memodict=None):
        new_obj = type(self).__new__(type(self))
        for key in self.__dict__.keys():
            if key not in self._shallow_copied_vars.union({'_frozen_copy', '_is_frozen_copy_valid'}):
                new_obj.__dict__[key] = cp.deepcopy(self.__dict__[key], memodict)
            if key in self._shallow_copied_vars:
                new_obj.__dict__[key] = self.__dict__[key]

        return new_obj

    def _shallow_copy(self):

        new_obj = type(self).__new__(type(self))
        for key in self.__dict__.keys():
            if key not in {'_frozen_copy', '_is_frozen_copy_valid'}:
                new_obj.__dict__[key] = self.__dict__[key]
        return new_obj

    def __deepcopy__(self, memodict):
        return self._deep_copy(memodict)

    def get_properties(self):
        """
        Returns a dictionary containing all gettable properties of the object.self

        NEED TO WRITE something that metions this inthe baseclass documentation
        """

        objectclass = type(self)

        return {propname:objectclass.__getattribute__(propname).__get__(self)
                for propname, prop in self.__dict__.items()
                if isinstance(prop, property)}

    def set_properties(self, prop_dict):
        """
        Sets all settable properties with values in dict. Note that set function
        of the property should accept the value returned by the get function if
        using the dict returned by get_properties

        NEED TO WRITE something that metions this inthe baseclass documentation
        """
        all_settable_propnames = [
            (propname, prop)
            for propname, prop in self.__dict__
            if isinstance(prop, property) and prop.fset is not None]

        for propname, prop in all_settable_propnames:
            if propname in prop_dict:
                prop.fset(self, prop_dict[propname])


    @property
    def is_frozen(self):
        return self._is_frozen

    @property
    def is_built(self):
        return self._is_built

    @property
    def is_preprocessed(self):
        return self._is_preprocessed
    