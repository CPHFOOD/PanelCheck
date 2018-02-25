from util cimport numeric
from numpy cimport float64_t, double_t

cpdef numeric kth_smallest(numeric[:] a, Py_ssize_t k) nogil

cdef inline Py_ssize_t swap(numeric *a, numeric *b) nogil:
    cdef numeric t

    # cython doesn't allow pointer dereference so use array syntax
    t = a[0]
    a[0] = b[0]
    b[0] = t
    return 0

cdef enum TiebreakEnumType:
    TIEBREAK_AVERAGE
    TIEBREAK_MIN,
    TIEBREAK_MAX
    TIEBREAK_FIRST
    TIEBREAK_FIRST_DESCENDING
    TIEBREAK_DENSE
