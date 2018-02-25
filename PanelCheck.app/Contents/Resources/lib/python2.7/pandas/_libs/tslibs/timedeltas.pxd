# -*- coding: utf-8 -*-
# cython: profile=False

from cpython.datetime cimport timedelta

from numpy cimport int64_t, ndarray

# Exposed for tslib, not intended for outside use.
cdef parse_timedelta_string(object ts)
cpdef int64_t cast_from_unit(object ts, object unit) except? -1
cpdef int64_t delta_to_nanoseconds(delta) except? -1
cpdef convert_to_timedelta64(object ts, object unit)
cpdef array_to_timedelta64(ndarray[object] values, unit=*, errors=*)
