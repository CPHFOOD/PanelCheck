"""
Template for each `dtype` helper function for take

WARNING: DO NOT edit .pxi FILE directly, .pxi is generated from .pxi.in
"""

# ----------------------------------------------------------------------
# reshape
# ----------------------------------------------------------------------


@cython.wraparound(False)
@cython.boundscheck(False)
def unstack_uint8(ndarray[uint8_t, ndim=2] values,
                      ndarray[uint8_t, ndim=1] mask,
                      Py_ssize_t stride,
                      Py_ssize_t length,
                      Py_ssize_t width,
                      ndarray[uint8_t, ndim=2] new_values,
                      ndarray[uint8_t, ndim=2] new_mask):
    """
    transform long sorted_values to wide new_values

    Parameters
    ----------
    values : typed ndarray
    mask : boolean ndarray
    stride : int
    length : int
    width : int
    new_values : typed ndarray
        result array
    new_mask : boolean ndarray
        result mask

    """

    cdef:
        Py_ssize_t i, j, w, nulls, s, offset

    with nogil:

        for i in range(stride):

            nulls = 0
            for j in range(length):

                for w in range(width):

                    offset = j * width + w

                    if mask[offset]:
                        s = i * width + w
                        new_values[j, s] = values[offset - nulls, i]
                        new_mask[j, s] = 1
                    else:
                        nulls += 1


@cython.wraparound(False)
@cython.boundscheck(False)
def unstack_uint16(ndarray[uint16_t, ndim=2] values,
                      ndarray[uint8_t, ndim=1] mask,
                      Py_ssize_t stride,
                      Py_ssize_t length,
                      Py_ssize_t width,
                      ndarray[uint16_t, ndim=2] new_values,
                      ndarray[uint8_t, ndim=2] new_mask):
    """
    transform long sorted_values to wide new_values

    Parameters
    ----------
    values : typed ndarray
    mask : boolean ndarray
    stride : int
    length : int
    width : int
    new_values : typed ndarray
        result array
    new_mask : boolean ndarray
        result mask

    """

    cdef:
        Py_ssize_t i, j, w, nulls, s, offset

    with nogil:

        for i in range(stride):

            nulls = 0
            for j in range(length):

                for w in range(width):

                    offset = j * width + w

                    if mask[offset]:
                        s = i * width + w
                        new_values[j, s] = values[offset - nulls, i]
                        new_mask[j, s] = 1
                    else:
                        nulls += 1


@cython.wraparound(False)
@cython.boundscheck(False)
def unstack_uint32(ndarray[uint32_t, ndim=2] values,
                      ndarray[uint8_t, ndim=1] mask,
                      Py_ssize_t stride,
                      Py_ssize_t length,
                      Py_ssize_t width,
                      ndarray[uint32_t, ndim=2] new_values,
                      ndarray[uint8_t, ndim=2] new_mask):
    """
    transform long sorted_values to wide new_values

    Parameters
    ----------
    values : typed ndarray
    mask : boolean ndarray
    stride : int
    length : int
    width : int
    new_values : typed ndarray
        result array
    new_mask : boolean ndarray
        result mask

    """

    cdef:
        Py_ssize_t i, j, w, nulls, s, offset

    with nogil:

        for i in range(stride):

            nulls = 0
            for j in range(length):

                for w in range(width):

                    offset = j * width + w

                    if mask[offset]:
                        s = i * width + w
                        new_values[j, s] = values[offset - nulls, i]
                        new_mask[j, s] = 1
                    else:
                        nulls += 1


@cython.wraparound(False)
@cython.boundscheck(False)
def unstack_uint64(ndarray[uint64_t, ndim=2] values,
                      ndarray[uint8_t, ndim=1] mask,
                      Py_ssize_t stride,
                      Py_ssize_t length,
                      Py_ssize_t width,
                      ndarray[uint64_t, ndim=2] new_values,
                      ndarray[uint8_t, ndim=2] new_mask):
    """
    transform long sorted_values to wide new_values

    Parameters
    ----------
    values : typed ndarray
    mask : boolean ndarray
    stride : int
    length : int
    width : int
    new_values : typed ndarray
        result array
    new_mask : boolean ndarray
        result mask

    """

    cdef:
        Py_ssize_t i, j, w, nulls, s, offset

    with nogil:

        for i in range(stride):

            nulls = 0
            for j in range(length):

                for w in range(width):

                    offset = j * width + w

                    if mask[offset]:
                        s = i * width + w
                        new_values[j, s] = values[offset - nulls, i]
                        new_mask[j, s] = 1
                    else:
                        nulls += 1


@cython.wraparound(False)
@cython.boundscheck(False)
def unstack_int8(ndarray[int8_t, ndim=2] values,
                      ndarray[uint8_t, ndim=1] mask,
                      Py_ssize_t stride,
                      Py_ssize_t length,
                      Py_ssize_t width,
                      ndarray[int8_t, ndim=2] new_values,
                      ndarray[uint8_t, ndim=2] new_mask):
    """
    transform long sorted_values to wide new_values

    Parameters
    ----------
    values : typed ndarray
    mask : boolean ndarray
    stride : int
    length : int
    width : int
    new_values : typed ndarray
        result array
    new_mask : boolean ndarray
        result mask

    """

    cdef:
        Py_ssize_t i, j, w, nulls, s, offset

    with nogil:

        for i in range(stride):

            nulls = 0
            for j in range(length):

                for w in range(width):

                    offset = j * width + w

                    if mask[offset]:
                        s = i * width + w
                        new_values[j, s] = values[offset - nulls, i]
                        new_mask[j, s] = 1
                    else:
                        nulls += 1


@cython.wraparound(False)
@cython.boundscheck(False)
def unstack_int16(ndarray[int16_t, ndim=2] values,
                      ndarray[uint8_t, ndim=1] mask,
                      Py_ssize_t stride,
                      Py_ssize_t length,
                      Py_ssize_t width,
                      ndarray[int16_t, ndim=2] new_values,
                      ndarray[uint8_t, ndim=2] new_mask):
    """
    transform long sorted_values to wide new_values

    Parameters
    ----------
    values : typed ndarray
    mask : boolean ndarray
    stride : int
    length : int
    width : int
    new_values : typed ndarray
        result array
    new_mask : boolean ndarray
        result mask

    """

    cdef:
        Py_ssize_t i, j, w, nulls, s, offset

    with nogil:

        for i in range(stride):

            nulls = 0
            for j in range(length):

                for w in range(width):

                    offset = j * width + w

                    if mask[offset]:
                        s = i * width + w
                        new_values[j, s] = values[offset - nulls, i]
                        new_mask[j, s] = 1
                    else:
                        nulls += 1


@cython.wraparound(False)
@cython.boundscheck(False)
def unstack_int32(ndarray[int32_t, ndim=2] values,
                      ndarray[uint8_t, ndim=1] mask,
                      Py_ssize_t stride,
                      Py_ssize_t length,
                      Py_ssize_t width,
                      ndarray[int32_t, ndim=2] new_values,
                      ndarray[uint8_t, ndim=2] new_mask):
    """
    transform long sorted_values to wide new_values

    Parameters
    ----------
    values : typed ndarray
    mask : boolean ndarray
    stride : int
    length : int
    width : int
    new_values : typed ndarray
        result array
    new_mask : boolean ndarray
        result mask

    """

    cdef:
        Py_ssize_t i, j, w, nulls, s, offset

    with nogil:

        for i in range(stride):

            nulls = 0
            for j in range(length):

                for w in range(width):

                    offset = j * width + w

                    if mask[offset]:
                        s = i * width + w
                        new_values[j, s] = values[offset - nulls, i]
                        new_mask[j, s] = 1
                    else:
                        nulls += 1


@cython.wraparound(False)
@cython.boundscheck(False)
def unstack_int64(ndarray[int64_t, ndim=2] values,
                      ndarray[uint8_t, ndim=1] mask,
                      Py_ssize_t stride,
                      Py_ssize_t length,
                      Py_ssize_t width,
                      ndarray[int64_t, ndim=2] new_values,
                      ndarray[uint8_t, ndim=2] new_mask):
    """
    transform long sorted_values to wide new_values

    Parameters
    ----------
    values : typed ndarray
    mask : boolean ndarray
    stride : int
    length : int
    width : int
    new_values : typed ndarray
        result array
    new_mask : boolean ndarray
        result mask

    """

    cdef:
        Py_ssize_t i, j, w, nulls, s, offset

    with nogil:

        for i in range(stride):

            nulls = 0
            for j in range(length):

                for w in range(width):

                    offset = j * width + w

                    if mask[offset]:
                        s = i * width + w
                        new_values[j, s] = values[offset - nulls, i]
                        new_mask[j, s] = 1
                    else:
                        nulls += 1


@cython.wraparound(False)
@cython.boundscheck(False)
def unstack_float32(ndarray[float32_t, ndim=2] values,
                      ndarray[uint8_t, ndim=1] mask,
                      Py_ssize_t stride,
                      Py_ssize_t length,
                      Py_ssize_t width,
                      ndarray[float32_t, ndim=2] new_values,
                      ndarray[uint8_t, ndim=2] new_mask):
    """
    transform long sorted_values to wide new_values

    Parameters
    ----------
    values : typed ndarray
    mask : boolean ndarray
    stride : int
    length : int
    width : int
    new_values : typed ndarray
        result array
    new_mask : boolean ndarray
        result mask

    """

    cdef:
        Py_ssize_t i, j, w, nulls, s, offset

    with nogil:

        for i in range(stride):

            nulls = 0
            for j in range(length):

                for w in range(width):

                    offset = j * width + w

                    if mask[offset]:
                        s = i * width + w
                        new_values[j, s] = values[offset - nulls, i]
                        new_mask[j, s] = 1
                    else:
                        nulls += 1


@cython.wraparound(False)
@cython.boundscheck(False)
def unstack_float64(ndarray[float64_t, ndim=2] values,
                      ndarray[uint8_t, ndim=1] mask,
                      Py_ssize_t stride,
                      Py_ssize_t length,
                      Py_ssize_t width,
                      ndarray[float64_t, ndim=2] new_values,
                      ndarray[uint8_t, ndim=2] new_mask):
    """
    transform long sorted_values to wide new_values

    Parameters
    ----------
    values : typed ndarray
    mask : boolean ndarray
    stride : int
    length : int
    width : int
    new_values : typed ndarray
        result array
    new_mask : boolean ndarray
        result mask

    """

    cdef:
        Py_ssize_t i, j, w, nulls, s, offset

    with nogil:

        for i in range(stride):

            nulls = 0
            for j in range(length):

                for w in range(width):

                    offset = j * width + w

                    if mask[offset]:
                        s = i * width + w
                        new_values[j, s] = values[offset - nulls, i]
                        new_mask[j, s] = 1
                    else:
                        nulls += 1


@cython.wraparound(False)
@cython.boundscheck(False)
def unstack_object(ndarray[object, ndim=2] values,
                      ndarray[uint8_t, ndim=1] mask,
                      Py_ssize_t stride,
                      Py_ssize_t length,
                      Py_ssize_t width,
                      ndarray[object, ndim=2] new_values,
                      ndarray[uint8_t, ndim=2] new_mask):
    """
    transform long sorted_values to wide new_values

    Parameters
    ----------
    values : typed ndarray
    mask : boolean ndarray
    stride : int
    length : int
    width : int
    new_values : typed ndarray
        result array
    new_mask : boolean ndarray
        result mask

    """

    cdef:
        Py_ssize_t i, j, w, nulls, s, offset

    if True:

        for i in range(stride):

            nulls = 0
            for j in range(length):

                for w in range(width):

                    offset = j * width + w

                    if mask[offset]:
                        s = i * width + w
                        new_values[j, s] = values[offset - nulls, i]
                        new_mask[j, s] = 1
                    else:
                        nulls += 1
