from .metaclass import MetaGenericBuilder

from abc import abstractmethod

class BaseGenericBuilder(metaclass=MetaGenericBuilder):

    # `built_properties` represents those properties that are only valid when the builder has been
    # built. This variable has to be overridden be classes that inherit the BaseGenericBuilder
    built_properties = []

    # This is a value that is used to perform builder identification. When creating a subclass of
    # builders it is prudent to assign that subclass a different type in order to distinguish it.
    builder_type = 'generic'

    def __init__(self):
        """
        Within this function, all the relevant data members are assigned. For now, no property that
        is indirect i.e. not directly represented by a data member, may be assigned.

        All arguments must be specified as explicitly defined keywords in order to be accessible to
        the IDE
        """
        self._is_mutable = True
        self._is_built = False
        self._is_preprocessed = False
        self._is_frozen = False
        pass

    def copy(self):
        """
        Creates a copy of the builder. Note that this does NOT perform a deep copy and is
        completely reliant on the assumption that no data member is mutated EVER.

        :returns: new builder that is the copy of this one.
        """
        new_obj = BaseGenericBuilder.__new__(self.__class__)
        for key, value in self.__dict__.items():
            new_obj.__dict__[key] = value
        return new_obj

    def copy_mutable(self):
        """
        This creates a mutable copy of the builder.

        NOTE:

        1.  While the properties of a mutable builder may be changed, they must still NOT BE
            MUTATED.

        :returns: new builder that is the mutable, unbuilt copy of self.
        """
        new_obj = self.copy()
        new_obj._is_mutable = True  # Don't EVER do this outside here
        return new_obj

    def set_frozen(self, frozen=True):
        """
        This freezes/unfreezes the given builder. Note that a builder can only be frozen/unfrozen
        if mutable/unbuilt. A frozen builder will perform a build only once after being frozen.
        
        :param frozen: set `True` to freeze and `False` to unfreeze, defaults to `True`

        :returns: `self` after having frozen it
        """
        if self._is_mutable and self._is_built:
            self._is_frozen = bool(frozen)
        elif self._is_mutable:
            raise AttributeError('Cannot alter frozen-ness of an unbuilt builder')
        else:
            raise AttributeError('Cannot alter frozen-ness of an immutable builder')
        return self

    def set_immutable(self):
        """
        Make the builder immutable. Note that this builder need not be in a built state. However,
        once the builder is immutable, one cannot call build() on it again, only build_copy().
        This function is useful in cases where one would like to enforce immutabiility without
        performing a full build.

        NOTE that the array is preprocessed before being made immutable. This is because it is
        expected that properties of an immutable builder be accessible. However, All property
        accesses trigger :func:`.BaseGenericBuilder.preprocess()` if the array is not pre-
        processed. Hence if an immutable array is not pre-processed, every property access will
        lead to an exception.

        :returns: `self` after having made it immutable
        """
        if self._is_mutable:
            self.preprocess()
        self._is_mutable = False
        return self

    def build_copy(self):
        """
        This function creates a mutable copy, performs a build on it (i.e. calls the build()
        function on it), and returns the resultant builder. Note that this function is the
        recommended way to build. This is because it applies to both mutable and immutable builders.
        """
        new_obj = self.copy_mutable()
        new_obj.build()
        return new_obj

    def build(self):
        """
        This is the function that is to be called to perform a build on a mutable builder. Note
        that it is best not to call this function and instead use `build_copy()` instead.

        NOTE: When this function is called, the object becomes immutable i.e. any further building
        must take place using `build_copy()`

        :returns: self after running build
        """
        if not self._is_mutable:
            raise AttributeError("An Immutable builder cannot run 'build()'")
        elif not self._is_frozen or not self._is_built:
            self.preprocess()
            self._build()
            self._is_built = True
        return self

    def preprocess(self):
        """
        Performs any preprocessing of the data members that would be required in order to make the
        internal variables of the builder consistent with the changed parameters
        """
        if not self._is_mutable:
            raise AttributeError("An Immutable builder cannot run preprocess()")
        elif not self._is_preprocessed:
            self._validate()
            self._preprocess()
            self._is_preprocessed = True

    # State retrieval functions.
    
    @property
    def is_mutable(self):
        return self._is_mutable

    @property
    def is_built(self):
        return self._is_built

    @property
    def is_preprocessed(self):
        return self._is_preprocessed

    @property
    def is_frozen(self):
        return self._is_frozen

    @abstractmethod
    def _build(self):
        """
        This function must be implemented in the derived class to perform the relevant building.
        """
        pass

    @abstractmethod
    def _preprocess(self):
        """
        This function must be implemented in the derived class to perform any preprocessing of the
        data that is required in order to make the internal variables of the builder consistent
        with the changed parameters
        """
        pass

    @abstractmethod
    def _validate(self):
        """
        This function is executed during preprocessing and must be implemented in the derived class
        in order to perform property validations that would be required.
        """
        pass
