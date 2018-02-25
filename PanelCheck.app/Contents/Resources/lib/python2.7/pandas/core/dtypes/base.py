"""Extend pandas with custom array types"""
import numpy as np

from pandas import compat
from pandas.errors import AbstractMethodError


class ExtensionDtype(object):
    """A custom data type, to be paired with an ExtensionArray.

    Notes
    -----
    The interface includes the following abstract methods that must
    be implemented by subclasses:

    * type
    * name
    * construct_from_string

    This class does not inherit from 'abc.ABCMeta' for performance reasons.
    Methods and properties required by the interface raise
    ``pandas.errors.AbstractMethodError`` and no ``register`` method is
    provided for registering virtual subclasses.
    """

    def __str__(self):
        return self.name

    def __eq__(self, other):
        """Check whether 'other' is equal to self.

        By default, 'other' is considered equal if

        * it's a string matching 'self.name'.
        * it's an instance of this type.

        Parameters
        ----------
        other : Any

        Returns
        -------
        bool
        """
        if isinstance(other, compat.string_types):
            return other == self.name
        elif isinstance(other, type(self)):
            return True
        else:
            return False

    def __ne__(self, other):
        return not self.__eq__(other)

    @property
    def type(self):
        # type: () -> type
        """The scalar type for the array, e.g. ``int``

        It's expected ``ExtensionArray[item]`` returns an instance
        of ``ExtensionDtype.type`` for scalar ``item``.
        """
        raise AbstractMethodError(self)

    @property
    def kind(self):
        # type () -> str
        """A character code (one of 'biufcmMOSUV'), default 'O'

        This should match the NumPy dtype used when the array is
        converted to an ndarray, which is probably 'O' for object if
        the extension type cannot be represented as a built-in NumPy
        type.

        See Also
        --------
        numpy.dtype.kind
        """
        return 'O'

    @property
    def name(self):
        # type: () -> str
        """A string identifying the data type.

        Will be used for display in, e.g. ``Series.dtype``
        """
        raise AbstractMethodError(self)

    @property
    def names(self):
        # type: () -> Optional[List[str]]
        """Ordered list of field names, or None if there are no fields.

        This is for compatibility with NumPy arrays, and may be removed in the
        future.
        """
        return None

    @classmethod
    def construct_from_string(cls, string):
        """Attempt to construct this type from a string.

        Parameters
        ----------
        string : str

        Returns
        -------
        self : instance of 'cls'

        Raises
        ------
        TypeError
            If a class cannot be constructed from this 'string'.

        Examples
        --------
        If the extension dtype can be constructed without any arguments,
        the following may be an adequate implementation.

        >>> @classmethod
        ... def construct_from_string(cls, string)
        ...     if string == cls.name:
        ...         return cls()
        ...     else:
        ...         raise TypeError("Cannot construct a '{}' from "
        ...                         "'{}'".format(cls, string))
        """
        raise AbstractMethodError(cls)

    @classmethod
    def is_dtype(cls, dtype):
        """Check if we match 'dtype'.

        Parameters
        ----------
        dtype : object
            The object to check.

        Returns
        -------
        is_dtype : bool

        Notes
        -----
        The default implementation is True if

        1. ``cls.construct_from_string(dtype)`` is an instance
           of ``cls``.
        2. ``dtype`` is an object and is an instance of ``cls``
        3. ``dtype`` has a ``dtype`` attribute, and any of the above
           conditions is true for ``dtype.dtype``.
        """
        dtype = getattr(dtype, 'dtype', dtype)

        if isinstance(dtype, np.dtype):
            return False
        elif dtype is None:
            return False
        elif isinstance(dtype, cls):
            return True
        try:
            return cls.construct_from_string(dtype) is not None
        except TypeError:
            return False
