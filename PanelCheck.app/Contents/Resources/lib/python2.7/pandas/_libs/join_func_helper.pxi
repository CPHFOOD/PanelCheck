# cython: boundscheck=False, wraparound=False
"""
Template for each `dtype` helper function for hashtable

WARNING: DO NOT edit .pxi FILE directly, .pxi is generated from .pxi.in
"""

#----------------------------------------------------------------------
# asof_join_by
#----------------------------------------------------------------------

from hashtable cimport PyObjectHashTable, UInt64HashTable, Int64HashTable


def asof_join_backward_uint8_t_by_object(
        ndarray[uint8_t] left_values,
        ndarray[uint8_t] right_values,
        ndarray[object] left_by_values,
        ndarray[object] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        uint8_t tolerance_ = 0
        uint8_t diff = 0
        PyObjectHashTable hash_table
        object by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = PyObjectHashTable(right_size)

    right_pos = 0
    for left_pos in range(left_size):
        # restart right_pos if it went negative in a previous iteration
        if right_pos < 0:
            right_pos = 0

        # find last position in right whose value is less than left's
        if allow_exact_matches:
            while right_pos < right_size and\
                right_values[right_pos] <= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        else:
            while right_pos < right_size and\
                right_values[right_pos] < left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        right_pos -= 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = left_values[left_pos] - right_values[found_right_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_forward_uint8_t_by_object(
        ndarray[uint8_t] left_values,
        ndarray[uint8_t] right_values,
        ndarray[object] left_by_values,
        ndarray[object] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        uint8_t tolerance_ = 0
        uint8_t diff = 0
        PyObjectHashTable hash_table
        object by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = PyObjectHashTable(right_size)

    right_pos = right_size - 1
    for left_pos in range(left_size - 1, -1, -1):
        # restart right_pos if it went over in a previous iteration
        if right_pos == right_size:
            right_pos = right_size - 1

        # find first position in right whose value is greater than left's
        if allow_exact_matches:
            while right_pos >= 0 and\
                right_values[right_pos] >= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        else:
            while right_pos >= 0 and\
                right_values[right_pos] > left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        right_pos += 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = right_values[found_right_pos] - left_values[left_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_nearest_uint8_t_by_object(
        ndarray[uint8_t] left_values,
        ndarray[uint8_t] right_values,
        ndarray[object] left_by_values,
        ndarray[object] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_size, right_size, i
        ndarray[int64_t] left_indexer, right_indexer, bli, bri, fli, fri
        uint8_t bdiff, fdiff

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    # search both forward and backward
    bli, bri =\
        asof_join_backward_uint8_t_by_object(left_values,
                                                        right_values,
                                                        left_by_values,
                                                        right_by_values,
                                                        allow_exact_matches,
                                                        tolerance)
    fli, fri =\
        asof_join_forward_uint8_t_by_object(left_values,
                                                       right_values,
                                                       left_by_values,
                                                       right_by_values,
                                                       allow_exact_matches,
                                                       tolerance)

    for i in range(len(bri)):
        # choose timestamp from right with smaller difference
        if bri[i] != -1 and fri[i] != -1:
            bdiff = left_values[bli[i]] - right_values[bri[i]]
            fdiff = right_values[fri[i]] - left_values[fli[i]]
            right_indexer[i] = bri[i] if bdiff <= fdiff else fri[i]
        else:
            right_indexer[i] = bri[i] if bri[i] != -1 else fri[i]
        left_indexer[i] = bli[i]

    return left_indexer, right_indexer


def asof_join_backward_uint16_t_by_object(
        ndarray[uint16_t] left_values,
        ndarray[uint16_t] right_values,
        ndarray[object] left_by_values,
        ndarray[object] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        uint16_t tolerance_ = 0
        uint16_t diff = 0
        PyObjectHashTable hash_table
        object by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = PyObjectHashTable(right_size)

    right_pos = 0
    for left_pos in range(left_size):
        # restart right_pos if it went negative in a previous iteration
        if right_pos < 0:
            right_pos = 0

        # find last position in right whose value is less than left's
        if allow_exact_matches:
            while right_pos < right_size and\
                right_values[right_pos] <= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        else:
            while right_pos < right_size and\
                right_values[right_pos] < left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        right_pos -= 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = left_values[left_pos] - right_values[found_right_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_forward_uint16_t_by_object(
        ndarray[uint16_t] left_values,
        ndarray[uint16_t] right_values,
        ndarray[object] left_by_values,
        ndarray[object] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        uint16_t tolerance_ = 0
        uint16_t diff = 0
        PyObjectHashTable hash_table
        object by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = PyObjectHashTable(right_size)

    right_pos = right_size - 1
    for left_pos in range(left_size - 1, -1, -1):
        # restart right_pos if it went over in a previous iteration
        if right_pos == right_size:
            right_pos = right_size - 1

        # find first position in right whose value is greater than left's
        if allow_exact_matches:
            while right_pos >= 0 and\
                right_values[right_pos] >= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        else:
            while right_pos >= 0 and\
                right_values[right_pos] > left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        right_pos += 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = right_values[found_right_pos] - left_values[left_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_nearest_uint16_t_by_object(
        ndarray[uint16_t] left_values,
        ndarray[uint16_t] right_values,
        ndarray[object] left_by_values,
        ndarray[object] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_size, right_size, i
        ndarray[int64_t] left_indexer, right_indexer, bli, bri, fli, fri
        uint16_t bdiff, fdiff

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    # search both forward and backward
    bli, bri =\
        asof_join_backward_uint16_t_by_object(left_values,
                                                        right_values,
                                                        left_by_values,
                                                        right_by_values,
                                                        allow_exact_matches,
                                                        tolerance)
    fli, fri =\
        asof_join_forward_uint16_t_by_object(left_values,
                                                       right_values,
                                                       left_by_values,
                                                       right_by_values,
                                                       allow_exact_matches,
                                                       tolerance)

    for i in range(len(bri)):
        # choose timestamp from right with smaller difference
        if bri[i] != -1 and fri[i] != -1:
            bdiff = left_values[bli[i]] - right_values[bri[i]]
            fdiff = right_values[fri[i]] - left_values[fli[i]]
            right_indexer[i] = bri[i] if bdiff <= fdiff else fri[i]
        else:
            right_indexer[i] = bri[i] if bri[i] != -1 else fri[i]
        left_indexer[i] = bli[i]

    return left_indexer, right_indexer


def asof_join_backward_uint32_t_by_object(
        ndarray[uint32_t] left_values,
        ndarray[uint32_t] right_values,
        ndarray[object] left_by_values,
        ndarray[object] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        uint32_t tolerance_ = 0
        uint32_t diff = 0
        PyObjectHashTable hash_table
        object by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = PyObjectHashTable(right_size)

    right_pos = 0
    for left_pos in range(left_size):
        # restart right_pos if it went negative in a previous iteration
        if right_pos < 0:
            right_pos = 0

        # find last position in right whose value is less than left's
        if allow_exact_matches:
            while right_pos < right_size and\
                right_values[right_pos] <= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        else:
            while right_pos < right_size and\
                right_values[right_pos] < left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        right_pos -= 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = left_values[left_pos] - right_values[found_right_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_forward_uint32_t_by_object(
        ndarray[uint32_t] left_values,
        ndarray[uint32_t] right_values,
        ndarray[object] left_by_values,
        ndarray[object] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        uint32_t tolerance_ = 0
        uint32_t diff = 0
        PyObjectHashTable hash_table
        object by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = PyObjectHashTable(right_size)

    right_pos = right_size - 1
    for left_pos in range(left_size - 1, -1, -1):
        # restart right_pos if it went over in a previous iteration
        if right_pos == right_size:
            right_pos = right_size - 1

        # find first position in right whose value is greater than left's
        if allow_exact_matches:
            while right_pos >= 0 and\
                right_values[right_pos] >= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        else:
            while right_pos >= 0 and\
                right_values[right_pos] > left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        right_pos += 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = right_values[found_right_pos] - left_values[left_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_nearest_uint32_t_by_object(
        ndarray[uint32_t] left_values,
        ndarray[uint32_t] right_values,
        ndarray[object] left_by_values,
        ndarray[object] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_size, right_size, i
        ndarray[int64_t] left_indexer, right_indexer, bli, bri, fli, fri
        uint32_t bdiff, fdiff

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    # search both forward and backward
    bli, bri =\
        asof_join_backward_uint32_t_by_object(left_values,
                                                        right_values,
                                                        left_by_values,
                                                        right_by_values,
                                                        allow_exact_matches,
                                                        tolerance)
    fli, fri =\
        asof_join_forward_uint32_t_by_object(left_values,
                                                       right_values,
                                                       left_by_values,
                                                       right_by_values,
                                                       allow_exact_matches,
                                                       tolerance)

    for i in range(len(bri)):
        # choose timestamp from right with smaller difference
        if bri[i] != -1 and fri[i] != -1:
            bdiff = left_values[bli[i]] - right_values[bri[i]]
            fdiff = right_values[fri[i]] - left_values[fli[i]]
            right_indexer[i] = bri[i] if bdiff <= fdiff else fri[i]
        else:
            right_indexer[i] = bri[i] if bri[i] != -1 else fri[i]
        left_indexer[i] = bli[i]

    return left_indexer, right_indexer


def asof_join_backward_uint64_t_by_object(
        ndarray[uint64_t] left_values,
        ndarray[uint64_t] right_values,
        ndarray[object] left_by_values,
        ndarray[object] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        uint64_t tolerance_ = 0
        uint64_t diff = 0
        PyObjectHashTable hash_table
        object by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = PyObjectHashTable(right_size)

    right_pos = 0
    for left_pos in range(left_size):
        # restart right_pos if it went negative in a previous iteration
        if right_pos < 0:
            right_pos = 0

        # find last position in right whose value is less than left's
        if allow_exact_matches:
            while right_pos < right_size and\
                right_values[right_pos] <= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        else:
            while right_pos < right_size and\
                right_values[right_pos] < left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        right_pos -= 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = left_values[left_pos] - right_values[found_right_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_forward_uint64_t_by_object(
        ndarray[uint64_t] left_values,
        ndarray[uint64_t] right_values,
        ndarray[object] left_by_values,
        ndarray[object] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        uint64_t tolerance_ = 0
        uint64_t diff = 0
        PyObjectHashTable hash_table
        object by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = PyObjectHashTable(right_size)

    right_pos = right_size - 1
    for left_pos in range(left_size - 1, -1, -1):
        # restart right_pos if it went over in a previous iteration
        if right_pos == right_size:
            right_pos = right_size - 1

        # find first position in right whose value is greater than left's
        if allow_exact_matches:
            while right_pos >= 0 and\
                right_values[right_pos] >= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        else:
            while right_pos >= 0 and\
                right_values[right_pos] > left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        right_pos += 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = right_values[found_right_pos] - left_values[left_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_nearest_uint64_t_by_object(
        ndarray[uint64_t] left_values,
        ndarray[uint64_t] right_values,
        ndarray[object] left_by_values,
        ndarray[object] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_size, right_size, i
        ndarray[int64_t] left_indexer, right_indexer, bli, bri, fli, fri
        uint64_t bdiff, fdiff

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    # search both forward and backward
    bli, bri =\
        asof_join_backward_uint64_t_by_object(left_values,
                                                        right_values,
                                                        left_by_values,
                                                        right_by_values,
                                                        allow_exact_matches,
                                                        tolerance)
    fli, fri =\
        asof_join_forward_uint64_t_by_object(left_values,
                                                       right_values,
                                                       left_by_values,
                                                       right_by_values,
                                                       allow_exact_matches,
                                                       tolerance)

    for i in range(len(bri)):
        # choose timestamp from right with smaller difference
        if bri[i] != -1 and fri[i] != -1:
            bdiff = left_values[bli[i]] - right_values[bri[i]]
            fdiff = right_values[fri[i]] - left_values[fli[i]]
            right_indexer[i] = bri[i] if bdiff <= fdiff else fri[i]
        else:
            right_indexer[i] = bri[i] if bri[i] != -1 else fri[i]
        left_indexer[i] = bli[i]

    return left_indexer, right_indexer


def asof_join_backward_int8_t_by_object(
        ndarray[int8_t] left_values,
        ndarray[int8_t] right_values,
        ndarray[object] left_by_values,
        ndarray[object] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        int8_t tolerance_ = 0
        int8_t diff = 0
        PyObjectHashTable hash_table
        object by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = PyObjectHashTable(right_size)

    right_pos = 0
    for left_pos in range(left_size):
        # restart right_pos if it went negative in a previous iteration
        if right_pos < 0:
            right_pos = 0

        # find last position in right whose value is less than left's
        if allow_exact_matches:
            while right_pos < right_size and\
                right_values[right_pos] <= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        else:
            while right_pos < right_size and\
                right_values[right_pos] < left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        right_pos -= 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = left_values[left_pos] - right_values[found_right_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_forward_int8_t_by_object(
        ndarray[int8_t] left_values,
        ndarray[int8_t] right_values,
        ndarray[object] left_by_values,
        ndarray[object] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        int8_t tolerance_ = 0
        int8_t diff = 0
        PyObjectHashTable hash_table
        object by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = PyObjectHashTable(right_size)

    right_pos = right_size - 1
    for left_pos in range(left_size - 1, -1, -1):
        # restart right_pos if it went over in a previous iteration
        if right_pos == right_size:
            right_pos = right_size - 1

        # find first position in right whose value is greater than left's
        if allow_exact_matches:
            while right_pos >= 0 and\
                right_values[right_pos] >= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        else:
            while right_pos >= 0 and\
                right_values[right_pos] > left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        right_pos += 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = right_values[found_right_pos] - left_values[left_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_nearest_int8_t_by_object(
        ndarray[int8_t] left_values,
        ndarray[int8_t] right_values,
        ndarray[object] left_by_values,
        ndarray[object] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_size, right_size, i
        ndarray[int64_t] left_indexer, right_indexer, bli, bri, fli, fri
        int8_t bdiff, fdiff

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    # search both forward and backward
    bli, bri =\
        asof_join_backward_int8_t_by_object(left_values,
                                                        right_values,
                                                        left_by_values,
                                                        right_by_values,
                                                        allow_exact_matches,
                                                        tolerance)
    fli, fri =\
        asof_join_forward_int8_t_by_object(left_values,
                                                       right_values,
                                                       left_by_values,
                                                       right_by_values,
                                                       allow_exact_matches,
                                                       tolerance)

    for i in range(len(bri)):
        # choose timestamp from right with smaller difference
        if bri[i] != -1 and fri[i] != -1:
            bdiff = left_values[bli[i]] - right_values[bri[i]]
            fdiff = right_values[fri[i]] - left_values[fli[i]]
            right_indexer[i] = bri[i] if bdiff <= fdiff else fri[i]
        else:
            right_indexer[i] = bri[i] if bri[i] != -1 else fri[i]
        left_indexer[i] = bli[i]

    return left_indexer, right_indexer


def asof_join_backward_int16_t_by_object(
        ndarray[int16_t] left_values,
        ndarray[int16_t] right_values,
        ndarray[object] left_by_values,
        ndarray[object] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        int16_t tolerance_ = 0
        int16_t diff = 0
        PyObjectHashTable hash_table
        object by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = PyObjectHashTable(right_size)

    right_pos = 0
    for left_pos in range(left_size):
        # restart right_pos if it went negative in a previous iteration
        if right_pos < 0:
            right_pos = 0

        # find last position in right whose value is less than left's
        if allow_exact_matches:
            while right_pos < right_size and\
                right_values[right_pos] <= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        else:
            while right_pos < right_size and\
                right_values[right_pos] < left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        right_pos -= 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = left_values[left_pos] - right_values[found_right_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_forward_int16_t_by_object(
        ndarray[int16_t] left_values,
        ndarray[int16_t] right_values,
        ndarray[object] left_by_values,
        ndarray[object] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        int16_t tolerance_ = 0
        int16_t diff = 0
        PyObjectHashTable hash_table
        object by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = PyObjectHashTable(right_size)

    right_pos = right_size - 1
    for left_pos in range(left_size - 1, -1, -1):
        # restart right_pos if it went over in a previous iteration
        if right_pos == right_size:
            right_pos = right_size - 1

        # find first position in right whose value is greater than left's
        if allow_exact_matches:
            while right_pos >= 0 and\
                right_values[right_pos] >= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        else:
            while right_pos >= 0 and\
                right_values[right_pos] > left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        right_pos += 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = right_values[found_right_pos] - left_values[left_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_nearest_int16_t_by_object(
        ndarray[int16_t] left_values,
        ndarray[int16_t] right_values,
        ndarray[object] left_by_values,
        ndarray[object] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_size, right_size, i
        ndarray[int64_t] left_indexer, right_indexer, bli, bri, fli, fri
        int16_t bdiff, fdiff

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    # search both forward and backward
    bli, bri =\
        asof_join_backward_int16_t_by_object(left_values,
                                                        right_values,
                                                        left_by_values,
                                                        right_by_values,
                                                        allow_exact_matches,
                                                        tolerance)
    fli, fri =\
        asof_join_forward_int16_t_by_object(left_values,
                                                       right_values,
                                                       left_by_values,
                                                       right_by_values,
                                                       allow_exact_matches,
                                                       tolerance)

    for i in range(len(bri)):
        # choose timestamp from right with smaller difference
        if bri[i] != -1 and fri[i] != -1:
            bdiff = left_values[bli[i]] - right_values[bri[i]]
            fdiff = right_values[fri[i]] - left_values[fli[i]]
            right_indexer[i] = bri[i] if bdiff <= fdiff else fri[i]
        else:
            right_indexer[i] = bri[i] if bri[i] != -1 else fri[i]
        left_indexer[i] = bli[i]

    return left_indexer, right_indexer


def asof_join_backward_int32_t_by_object(
        ndarray[int32_t] left_values,
        ndarray[int32_t] right_values,
        ndarray[object] left_by_values,
        ndarray[object] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        int32_t tolerance_ = 0
        int32_t diff = 0
        PyObjectHashTable hash_table
        object by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = PyObjectHashTable(right_size)

    right_pos = 0
    for left_pos in range(left_size):
        # restart right_pos if it went negative in a previous iteration
        if right_pos < 0:
            right_pos = 0

        # find last position in right whose value is less than left's
        if allow_exact_matches:
            while right_pos < right_size and\
                right_values[right_pos] <= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        else:
            while right_pos < right_size and\
                right_values[right_pos] < left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        right_pos -= 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = left_values[left_pos] - right_values[found_right_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_forward_int32_t_by_object(
        ndarray[int32_t] left_values,
        ndarray[int32_t] right_values,
        ndarray[object] left_by_values,
        ndarray[object] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        int32_t tolerance_ = 0
        int32_t diff = 0
        PyObjectHashTable hash_table
        object by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = PyObjectHashTable(right_size)

    right_pos = right_size - 1
    for left_pos in range(left_size - 1, -1, -1):
        # restart right_pos if it went over in a previous iteration
        if right_pos == right_size:
            right_pos = right_size - 1

        # find first position in right whose value is greater than left's
        if allow_exact_matches:
            while right_pos >= 0 and\
                right_values[right_pos] >= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        else:
            while right_pos >= 0 and\
                right_values[right_pos] > left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        right_pos += 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = right_values[found_right_pos] - left_values[left_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_nearest_int32_t_by_object(
        ndarray[int32_t] left_values,
        ndarray[int32_t] right_values,
        ndarray[object] left_by_values,
        ndarray[object] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_size, right_size, i
        ndarray[int64_t] left_indexer, right_indexer, bli, bri, fli, fri
        int32_t bdiff, fdiff

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    # search both forward and backward
    bli, bri =\
        asof_join_backward_int32_t_by_object(left_values,
                                                        right_values,
                                                        left_by_values,
                                                        right_by_values,
                                                        allow_exact_matches,
                                                        tolerance)
    fli, fri =\
        asof_join_forward_int32_t_by_object(left_values,
                                                       right_values,
                                                       left_by_values,
                                                       right_by_values,
                                                       allow_exact_matches,
                                                       tolerance)

    for i in range(len(bri)):
        # choose timestamp from right with smaller difference
        if bri[i] != -1 and fri[i] != -1:
            bdiff = left_values[bli[i]] - right_values[bri[i]]
            fdiff = right_values[fri[i]] - left_values[fli[i]]
            right_indexer[i] = bri[i] if bdiff <= fdiff else fri[i]
        else:
            right_indexer[i] = bri[i] if bri[i] != -1 else fri[i]
        left_indexer[i] = bli[i]

    return left_indexer, right_indexer


def asof_join_backward_int64_t_by_object(
        ndarray[int64_t] left_values,
        ndarray[int64_t] right_values,
        ndarray[object] left_by_values,
        ndarray[object] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        int64_t tolerance_ = 0
        int64_t diff = 0
        PyObjectHashTable hash_table
        object by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = PyObjectHashTable(right_size)

    right_pos = 0
    for left_pos in range(left_size):
        # restart right_pos if it went negative in a previous iteration
        if right_pos < 0:
            right_pos = 0

        # find last position in right whose value is less than left's
        if allow_exact_matches:
            while right_pos < right_size and\
                right_values[right_pos] <= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        else:
            while right_pos < right_size and\
                right_values[right_pos] < left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        right_pos -= 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = left_values[left_pos] - right_values[found_right_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_forward_int64_t_by_object(
        ndarray[int64_t] left_values,
        ndarray[int64_t] right_values,
        ndarray[object] left_by_values,
        ndarray[object] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        int64_t tolerance_ = 0
        int64_t diff = 0
        PyObjectHashTable hash_table
        object by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = PyObjectHashTable(right_size)

    right_pos = right_size - 1
    for left_pos in range(left_size - 1, -1, -1):
        # restart right_pos if it went over in a previous iteration
        if right_pos == right_size:
            right_pos = right_size - 1

        # find first position in right whose value is greater than left's
        if allow_exact_matches:
            while right_pos >= 0 and\
                right_values[right_pos] >= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        else:
            while right_pos >= 0 and\
                right_values[right_pos] > left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        right_pos += 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = right_values[found_right_pos] - left_values[left_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_nearest_int64_t_by_object(
        ndarray[int64_t] left_values,
        ndarray[int64_t] right_values,
        ndarray[object] left_by_values,
        ndarray[object] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_size, right_size, i
        ndarray[int64_t] left_indexer, right_indexer, bli, bri, fli, fri
        int64_t bdiff, fdiff

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    # search both forward and backward
    bli, bri =\
        asof_join_backward_int64_t_by_object(left_values,
                                                        right_values,
                                                        left_by_values,
                                                        right_by_values,
                                                        allow_exact_matches,
                                                        tolerance)
    fli, fri =\
        asof_join_forward_int64_t_by_object(left_values,
                                                       right_values,
                                                       left_by_values,
                                                       right_by_values,
                                                       allow_exact_matches,
                                                       tolerance)

    for i in range(len(bri)):
        # choose timestamp from right with smaller difference
        if bri[i] != -1 and fri[i] != -1:
            bdiff = left_values[bli[i]] - right_values[bri[i]]
            fdiff = right_values[fri[i]] - left_values[fli[i]]
            right_indexer[i] = bri[i] if bdiff <= fdiff else fri[i]
        else:
            right_indexer[i] = bri[i] if bri[i] != -1 else fri[i]
        left_indexer[i] = bli[i]

    return left_indexer, right_indexer


def asof_join_backward_float_by_object(
        ndarray[float] left_values,
        ndarray[float] right_values,
        ndarray[object] left_by_values,
        ndarray[object] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        float tolerance_ = 0
        float diff = 0
        PyObjectHashTable hash_table
        object by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = PyObjectHashTable(right_size)

    right_pos = 0
    for left_pos in range(left_size):
        # restart right_pos if it went negative in a previous iteration
        if right_pos < 0:
            right_pos = 0

        # find last position in right whose value is less than left's
        if allow_exact_matches:
            while right_pos < right_size and\
                right_values[right_pos] <= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        else:
            while right_pos < right_size and\
                right_values[right_pos] < left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        right_pos -= 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = left_values[left_pos] - right_values[found_right_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_forward_float_by_object(
        ndarray[float] left_values,
        ndarray[float] right_values,
        ndarray[object] left_by_values,
        ndarray[object] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        float tolerance_ = 0
        float diff = 0
        PyObjectHashTable hash_table
        object by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = PyObjectHashTable(right_size)

    right_pos = right_size - 1
    for left_pos in range(left_size - 1, -1, -1):
        # restart right_pos if it went over in a previous iteration
        if right_pos == right_size:
            right_pos = right_size - 1

        # find first position in right whose value is greater than left's
        if allow_exact_matches:
            while right_pos >= 0 and\
                right_values[right_pos] >= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        else:
            while right_pos >= 0 and\
                right_values[right_pos] > left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        right_pos += 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = right_values[found_right_pos] - left_values[left_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_nearest_float_by_object(
        ndarray[float] left_values,
        ndarray[float] right_values,
        ndarray[object] left_by_values,
        ndarray[object] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_size, right_size, i
        ndarray[int64_t] left_indexer, right_indexer, bli, bri, fli, fri
        float bdiff, fdiff

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    # search both forward and backward
    bli, bri =\
        asof_join_backward_float_by_object(left_values,
                                                        right_values,
                                                        left_by_values,
                                                        right_by_values,
                                                        allow_exact_matches,
                                                        tolerance)
    fli, fri =\
        asof_join_forward_float_by_object(left_values,
                                                       right_values,
                                                       left_by_values,
                                                       right_by_values,
                                                       allow_exact_matches,
                                                       tolerance)

    for i in range(len(bri)):
        # choose timestamp from right with smaller difference
        if bri[i] != -1 and fri[i] != -1:
            bdiff = left_values[bli[i]] - right_values[bri[i]]
            fdiff = right_values[fri[i]] - left_values[fli[i]]
            right_indexer[i] = bri[i] if bdiff <= fdiff else fri[i]
        else:
            right_indexer[i] = bri[i] if bri[i] != -1 else fri[i]
        left_indexer[i] = bli[i]

    return left_indexer, right_indexer


def asof_join_backward_double_by_object(
        ndarray[double] left_values,
        ndarray[double] right_values,
        ndarray[object] left_by_values,
        ndarray[object] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        double tolerance_ = 0
        double diff = 0
        PyObjectHashTable hash_table
        object by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = PyObjectHashTable(right_size)

    right_pos = 0
    for left_pos in range(left_size):
        # restart right_pos if it went negative in a previous iteration
        if right_pos < 0:
            right_pos = 0

        # find last position in right whose value is less than left's
        if allow_exact_matches:
            while right_pos < right_size and\
                right_values[right_pos] <= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        else:
            while right_pos < right_size and\
                right_values[right_pos] < left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        right_pos -= 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = left_values[left_pos] - right_values[found_right_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_forward_double_by_object(
        ndarray[double] left_values,
        ndarray[double] right_values,
        ndarray[object] left_by_values,
        ndarray[object] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        double tolerance_ = 0
        double diff = 0
        PyObjectHashTable hash_table
        object by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = PyObjectHashTable(right_size)

    right_pos = right_size - 1
    for left_pos in range(left_size - 1, -1, -1):
        # restart right_pos if it went over in a previous iteration
        if right_pos == right_size:
            right_pos = right_size - 1

        # find first position in right whose value is greater than left's
        if allow_exact_matches:
            while right_pos >= 0 and\
                right_values[right_pos] >= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        else:
            while right_pos >= 0 and\
                right_values[right_pos] > left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        right_pos += 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = right_values[found_right_pos] - left_values[left_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_nearest_double_by_object(
        ndarray[double] left_values,
        ndarray[double] right_values,
        ndarray[object] left_by_values,
        ndarray[object] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_size, right_size, i
        ndarray[int64_t] left_indexer, right_indexer, bli, bri, fli, fri
        double bdiff, fdiff

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    # search both forward and backward
    bli, bri =\
        asof_join_backward_double_by_object(left_values,
                                                        right_values,
                                                        left_by_values,
                                                        right_by_values,
                                                        allow_exact_matches,
                                                        tolerance)
    fli, fri =\
        asof_join_forward_double_by_object(left_values,
                                                       right_values,
                                                       left_by_values,
                                                       right_by_values,
                                                       allow_exact_matches,
                                                       tolerance)

    for i in range(len(bri)):
        # choose timestamp from right with smaller difference
        if bri[i] != -1 and fri[i] != -1:
            bdiff = left_values[bli[i]] - right_values[bri[i]]
            fdiff = right_values[fri[i]] - left_values[fli[i]]
            right_indexer[i] = bri[i] if bdiff <= fdiff else fri[i]
        else:
            right_indexer[i] = bri[i] if bri[i] != -1 else fri[i]
        left_indexer[i] = bli[i]

    return left_indexer, right_indexer


def asof_join_backward_uint8_t_by_int64_t(
        ndarray[uint8_t] left_values,
        ndarray[uint8_t] right_values,
        ndarray[int64_t] left_by_values,
        ndarray[int64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        uint8_t tolerance_ = 0
        uint8_t diff = 0
        Int64HashTable hash_table
        int64_t by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = Int64HashTable(right_size)

    right_pos = 0
    for left_pos in range(left_size):
        # restart right_pos if it went negative in a previous iteration
        if right_pos < 0:
            right_pos = 0

        # find last position in right whose value is less than left's
        if allow_exact_matches:
            while right_pos < right_size and\
                right_values[right_pos] <= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        else:
            while right_pos < right_size and\
                right_values[right_pos] < left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        right_pos -= 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = left_values[left_pos] - right_values[found_right_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_forward_uint8_t_by_int64_t(
        ndarray[uint8_t] left_values,
        ndarray[uint8_t] right_values,
        ndarray[int64_t] left_by_values,
        ndarray[int64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        uint8_t tolerance_ = 0
        uint8_t diff = 0
        Int64HashTable hash_table
        int64_t by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = Int64HashTable(right_size)

    right_pos = right_size - 1
    for left_pos in range(left_size - 1, -1, -1):
        # restart right_pos if it went over in a previous iteration
        if right_pos == right_size:
            right_pos = right_size - 1

        # find first position in right whose value is greater than left's
        if allow_exact_matches:
            while right_pos >= 0 and\
                right_values[right_pos] >= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        else:
            while right_pos >= 0 and\
                right_values[right_pos] > left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        right_pos += 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = right_values[found_right_pos] - left_values[left_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_nearest_uint8_t_by_int64_t(
        ndarray[uint8_t] left_values,
        ndarray[uint8_t] right_values,
        ndarray[int64_t] left_by_values,
        ndarray[int64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_size, right_size, i
        ndarray[int64_t] left_indexer, right_indexer, bli, bri, fli, fri
        uint8_t bdiff, fdiff

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    # search both forward and backward
    bli, bri =\
        asof_join_backward_uint8_t_by_int64_t(left_values,
                                                        right_values,
                                                        left_by_values,
                                                        right_by_values,
                                                        allow_exact_matches,
                                                        tolerance)
    fli, fri =\
        asof_join_forward_uint8_t_by_int64_t(left_values,
                                                       right_values,
                                                       left_by_values,
                                                       right_by_values,
                                                       allow_exact_matches,
                                                       tolerance)

    for i in range(len(bri)):
        # choose timestamp from right with smaller difference
        if bri[i] != -1 and fri[i] != -1:
            bdiff = left_values[bli[i]] - right_values[bri[i]]
            fdiff = right_values[fri[i]] - left_values[fli[i]]
            right_indexer[i] = bri[i] if bdiff <= fdiff else fri[i]
        else:
            right_indexer[i] = bri[i] if bri[i] != -1 else fri[i]
        left_indexer[i] = bli[i]

    return left_indexer, right_indexer


def asof_join_backward_uint16_t_by_int64_t(
        ndarray[uint16_t] left_values,
        ndarray[uint16_t] right_values,
        ndarray[int64_t] left_by_values,
        ndarray[int64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        uint16_t tolerance_ = 0
        uint16_t diff = 0
        Int64HashTable hash_table
        int64_t by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = Int64HashTable(right_size)

    right_pos = 0
    for left_pos in range(left_size):
        # restart right_pos if it went negative in a previous iteration
        if right_pos < 0:
            right_pos = 0

        # find last position in right whose value is less than left's
        if allow_exact_matches:
            while right_pos < right_size and\
                right_values[right_pos] <= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        else:
            while right_pos < right_size and\
                right_values[right_pos] < left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        right_pos -= 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = left_values[left_pos] - right_values[found_right_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_forward_uint16_t_by_int64_t(
        ndarray[uint16_t] left_values,
        ndarray[uint16_t] right_values,
        ndarray[int64_t] left_by_values,
        ndarray[int64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        uint16_t tolerance_ = 0
        uint16_t diff = 0
        Int64HashTable hash_table
        int64_t by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = Int64HashTable(right_size)

    right_pos = right_size - 1
    for left_pos in range(left_size - 1, -1, -1):
        # restart right_pos if it went over in a previous iteration
        if right_pos == right_size:
            right_pos = right_size - 1

        # find first position in right whose value is greater than left's
        if allow_exact_matches:
            while right_pos >= 0 and\
                right_values[right_pos] >= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        else:
            while right_pos >= 0 and\
                right_values[right_pos] > left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        right_pos += 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = right_values[found_right_pos] - left_values[left_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_nearest_uint16_t_by_int64_t(
        ndarray[uint16_t] left_values,
        ndarray[uint16_t] right_values,
        ndarray[int64_t] left_by_values,
        ndarray[int64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_size, right_size, i
        ndarray[int64_t] left_indexer, right_indexer, bli, bri, fli, fri
        uint16_t bdiff, fdiff

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    # search both forward and backward
    bli, bri =\
        asof_join_backward_uint16_t_by_int64_t(left_values,
                                                        right_values,
                                                        left_by_values,
                                                        right_by_values,
                                                        allow_exact_matches,
                                                        tolerance)
    fli, fri =\
        asof_join_forward_uint16_t_by_int64_t(left_values,
                                                       right_values,
                                                       left_by_values,
                                                       right_by_values,
                                                       allow_exact_matches,
                                                       tolerance)

    for i in range(len(bri)):
        # choose timestamp from right with smaller difference
        if bri[i] != -1 and fri[i] != -1:
            bdiff = left_values[bli[i]] - right_values[bri[i]]
            fdiff = right_values[fri[i]] - left_values[fli[i]]
            right_indexer[i] = bri[i] if bdiff <= fdiff else fri[i]
        else:
            right_indexer[i] = bri[i] if bri[i] != -1 else fri[i]
        left_indexer[i] = bli[i]

    return left_indexer, right_indexer


def asof_join_backward_uint32_t_by_int64_t(
        ndarray[uint32_t] left_values,
        ndarray[uint32_t] right_values,
        ndarray[int64_t] left_by_values,
        ndarray[int64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        uint32_t tolerance_ = 0
        uint32_t diff = 0
        Int64HashTable hash_table
        int64_t by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = Int64HashTable(right_size)

    right_pos = 0
    for left_pos in range(left_size):
        # restart right_pos if it went negative in a previous iteration
        if right_pos < 0:
            right_pos = 0

        # find last position in right whose value is less than left's
        if allow_exact_matches:
            while right_pos < right_size and\
                right_values[right_pos] <= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        else:
            while right_pos < right_size and\
                right_values[right_pos] < left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        right_pos -= 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = left_values[left_pos] - right_values[found_right_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_forward_uint32_t_by_int64_t(
        ndarray[uint32_t] left_values,
        ndarray[uint32_t] right_values,
        ndarray[int64_t] left_by_values,
        ndarray[int64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        uint32_t tolerance_ = 0
        uint32_t diff = 0
        Int64HashTable hash_table
        int64_t by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = Int64HashTable(right_size)

    right_pos = right_size - 1
    for left_pos in range(left_size - 1, -1, -1):
        # restart right_pos if it went over in a previous iteration
        if right_pos == right_size:
            right_pos = right_size - 1

        # find first position in right whose value is greater than left's
        if allow_exact_matches:
            while right_pos >= 0 and\
                right_values[right_pos] >= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        else:
            while right_pos >= 0 and\
                right_values[right_pos] > left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        right_pos += 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = right_values[found_right_pos] - left_values[left_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_nearest_uint32_t_by_int64_t(
        ndarray[uint32_t] left_values,
        ndarray[uint32_t] right_values,
        ndarray[int64_t] left_by_values,
        ndarray[int64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_size, right_size, i
        ndarray[int64_t] left_indexer, right_indexer, bli, bri, fli, fri
        uint32_t bdiff, fdiff

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    # search both forward and backward
    bli, bri =\
        asof_join_backward_uint32_t_by_int64_t(left_values,
                                                        right_values,
                                                        left_by_values,
                                                        right_by_values,
                                                        allow_exact_matches,
                                                        tolerance)
    fli, fri =\
        asof_join_forward_uint32_t_by_int64_t(left_values,
                                                       right_values,
                                                       left_by_values,
                                                       right_by_values,
                                                       allow_exact_matches,
                                                       tolerance)

    for i in range(len(bri)):
        # choose timestamp from right with smaller difference
        if bri[i] != -1 and fri[i] != -1:
            bdiff = left_values[bli[i]] - right_values[bri[i]]
            fdiff = right_values[fri[i]] - left_values[fli[i]]
            right_indexer[i] = bri[i] if bdiff <= fdiff else fri[i]
        else:
            right_indexer[i] = bri[i] if bri[i] != -1 else fri[i]
        left_indexer[i] = bli[i]

    return left_indexer, right_indexer


def asof_join_backward_uint64_t_by_int64_t(
        ndarray[uint64_t] left_values,
        ndarray[uint64_t] right_values,
        ndarray[int64_t] left_by_values,
        ndarray[int64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        uint64_t tolerance_ = 0
        uint64_t diff = 0
        Int64HashTable hash_table
        int64_t by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = Int64HashTable(right_size)

    right_pos = 0
    for left_pos in range(left_size):
        # restart right_pos if it went negative in a previous iteration
        if right_pos < 0:
            right_pos = 0

        # find last position in right whose value is less than left's
        if allow_exact_matches:
            while right_pos < right_size and\
                right_values[right_pos] <= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        else:
            while right_pos < right_size and\
                right_values[right_pos] < left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        right_pos -= 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = left_values[left_pos] - right_values[found_right_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_forward_uint64_t_by_int64_t(
        ndarray[uint64_t] left_values,
        ndarray[uint64_t] right_values,
        ndarray[int64_t] left_by_values,
        ndarray[int64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        uint64_t tolerance_ = 0
        uint64_t diff = 0
        Int64HashTable hash_table
        int64_t by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = Int64HashTable(right_size)

    right_pos = right_size - 1
    for left_pos in range(left_size - 1, -1, -1):
        # restart right_pos if it went over in a previous iteration
        if right_pos == right_size:
            right_pos = right_size - 1

        # find first position in right whose value is greater than left's
        if allow_exact_matches:
            while right_pos >= 0 and\
                right_values[right_pos] >= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        else:
            while right_pos >= 0 and\
                right_values[right_pos] > left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        right_pos += 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = right_values[found_right_pos] - left_values[left_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_nearest_uint64_t_by_int64_t(
        ndarray[uint64_t] left_values,
        ndarray[uint64_t] right_values,
        ndarray[int64_t] left_by_values,
        ndarray[int64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_size, right_size, i
        ndarray[int64_t] left_indexer, right_indexer, bli, bri, fli, fri
        uint64_t bdiff, fdiff

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    # search both forward and backward
    bli, bri =\
        asof_join_backward_uint64_t_by_int64_t(left_values,
                                                        right_values,
                                                        left_by_values,
                                                        right_by_values,
                                                        allow_exact_matches,
                                                        tolerance)
    fli, fri =\
        asof_join_forward_uint64_t_by_int64_t(left_values,
                                                       right_values,
                                                       left_by_values,
                                                       right_by_values,
                                                       allow_exact_matches,
                                                       tolerance)

    for i in range(len(bri)):
        # choose timestamp from right with smaller difference
        if bri[i] != -1 and fri[i] != -1:
            bdiff = left_values[bli[i]] - right_values[bri[i]]
            fdiff = right_values[fri[i]] - left_values[fli[i]]
            right_indexer[i] = bri[i] if bdiff <= fdiff else fri[i]
        else:
            right_indexer[i] = bri[i] if bri[i] != -1 else fri[i]
        left_indexer[i] = bli[i]

    return left_indexer, right_indexer


def asof_join_backward_int8_t_by_int64_t(
        ndarray[int8_t] left_values,
        ndarray[int8_t] right_values,
        ndarray[int64_t] left_by_values,
        ndarray[int64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        int8_t tolerance_ = 0
        int8_t diff = 0
        Int64HashTable hash_table
        int64_t by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = Int64HashTable(right_size)

    right_pos = 0
    for left_pos in range(left_size):
        # restart right_pos if it went negative in a previous iteration
        if right_pos < 0:
            right_pos = 0

        # find last position in right whose value is less than left's
        if allow_exact_matches:
            while right_pos < right_size and\
                right_values[right_pos] <= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        else:
            while right_pos < right_size and\
                right_values[right_pos] < left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        right_pos -= 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = left_values[left_pos] - right_values[found_right_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_forward_int8_t_by_int64_t(
        ndarray[int8_t] left_values,
        ndarray[int8_t] right_values,
        ndarray[int64_t] left_by_values,
        ndarray[int64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        int8_t tolerance_ = 0
        int8_t diff = 0
        Int64HashTable hash_table
        int64_t by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = Int64HashTable(right_size)

    right_pos = right_size - 1
    for left_pos in range(left_size - 1, -1, -1):
        # restart right_pos if it went over in a previous iteration
        if right_pos == right_size:
            right_pos = right_size - 1

        # find first position in right whose value is greater than left's
        if allow_exact_matches:
            while right_pos >= 0 and\
                right_values[right_pos] >= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        else:
            while right_pos >= 0 and\
                right_values[right_pos] > left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        right_pos += 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = right_values[found_right_pos] - left_values[left_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_nearest_int8_t_by_int64_t(
        ndarray[int8_t] left_values,
        ndarray[int8_t] right_values,
        ndarray[int64_t] left_by_values,
        ndarray[int64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_size, right_size, i
        ndarray[int64_t] left_indexer, right_indexer, bli, bri, fli, fri
        int8_t bdiff, fdiff

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    # search both forward and backward
    bli, bri =\
        asof_join_backward_int8_t_by_int64_t(left_values,
                                                        right_values,
                                                        left_by_values,
                                                        right_by_values,
                                                        allow_exact_matches,
                                                        tolerance)
    fli, fri =\
        asof_join_forward_int8_t_by_int64_t(left_values,
                                                       right_values,
                                                       left_by_values,
                                                       right_by_values,
                                                       allow_exact_matches,
                                                       tolerance)

    for i in range(len(bri)):
        # choose timestamp from right with smaller difference
        if bri[i] != -1 and fri[i] != -1:
            bdiff = left_values[bli[i]] - right_values[bri[i]]
            fdiff = right_values[fri[i]] - left_values[fli[i]]
            right_indexer[i] = bri[i] if bdiff <= fdiff else fri[i]
        else:
            right_indexer[i] = bri[i] if bri[i] != -1 else fri[i]
        left_indexer[i] = bli[i]

    return left_indexer, right_indexer


def asof_join_backward_int16_t_by_int64_t(
        ndarray[int16_t] left_values,
        ndarray[int16_t] right_values,
        ndarray[int64_t] left_by_values,
        ndarray[int64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        int16_t tolerance_ = 0
        int16_t diff = 0
        Int64HashTable hash_table
        int64_t by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = Int64HashTable(right_size)

    right_pos = 0
    for left_pos in range(left_size):
        # restart right_pos if it went negative in a previous iteration
        if right_pos < 0:
            right_pos = 0

        # find last position in right whose value is less than left's
        if allow_exact_matches:
            while right_pos < right_size and\
                right_values[right_pos] <= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        else:
            while right_pos < right_size and\
                right_values[right_pos] < left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        right_pos -= 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = left_values[left_pos] - right_values[found_right_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_forward_int16_t_by_int64_t(
        ndarray[int16_t] left_values,
        ndarray[int16_t] right_values,
        ndarray[int64_t] left_by_values,
        ndarray[int64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        int16_t tolerance_ = 0
        int16_t diff = 0
        Int64HashTable hash_table
        int64_t by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = Int64HashTable(right_size)

    right_pos = right_size - 1
    for left_pos in range(left_size - 1, -1, -1):
        # restart right_pos if it went over in a previous iteration
        if right_pos == right_size:
            right_pos = right_size - 1

        # find first position in right whose value is greater than left's
        if allow_exact_matches:
            while right_pos >= 0 and\
                right_values[right_pos] >= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        else:
            while right_pos >= 0 and\
                right_values[right_pos] > left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        right_pos += 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = right_values[found_right_pos] - left_values[left_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_nearest_int16_t_by_int64_t(
        ndarray[int16_t] left_values,
        ndarray[int16_t] right_values,
        ndarray[int64_t] left_by_values,
        ndarray[int64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_size, right_size, i
        ndarray[int64_t] left_indexer, right_indexer, bli, bri, fli, fri
        int16_t bdiff, fdiff

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    # search both forward and backward
    bli, bri =\
        asof_join_backward_int16_t_by_int64_t(left_values,
                                                        right_values,
                                                        left_by_values,
                                                        right_by_values,
                                                        allow_exact_matches,
                                                        tolerance)
    fli, fri =\
        asof_join_forward_int16_t_by_int64_t(left_values,
                                                       right_values,
                                                       left_by_values,
                                                       right_by_values,
                                                       allow_exact_matches,
                                                       tolerance)

    for i in range(len(bri)):
        # choose timestamp from right with smaller difference
        if bri[i] != -1 and fri[i] != -1:
            bdiff = left_values[bli[i]] - right_values[bri[i]]
            fdiff = right_values[fri[i]] - left_values[fli[i]]
            right_indexer[i] = bri[i] if bdiff <= fdiff else fri[i]
        else:
            right_indexer[i] = bri[i] if bri[i] != -1 else fri[i]
        left_indexer[i] = bli[i]

    return left_indexer, right_indexer


def asof_join_backward_int32_t_by_int64_t(
        ndarray[int32_t] left_values,
        ndarray[int32_t] right_values,
        ndarray[int64_t] left_by_values,
        ndarray[int64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        int32_t tolerance_ = 0
        int32_t diff = 0
        Int64HashTable hash_table
        int64_t by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = Int64HashTable(right_size)

    right_pos = 0
    for left_pos in range(left_size):
        # restart right_pos if it went negative in a previous iteration
        if right_pos < 0:
            right_pos = 0

        # find last position in right whose value is less than left's
        if allow_exact_matches:
            while right_pos < right_size and\
                right_values[right_pos] <= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        else:
            while right_pos < right_size and\
                right_values[right_pos] < left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        right_pos -= 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = left_values[left_pos] - right_values[found_right_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_forward_int32_t_by_int64_t(
        ndarray[int32_t] left_values,
        ndarray[int32_t] right_values,
        ndarray[int64_t] left_by_values,
        ndarray[int64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        int32_t tolerance_ = 0
        int32_t diff = 0
        Int64HashTable hash_table
        int64_t by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = Int64HashTable(right_size)

    right_pos = right_size - 1
    for left_pos in range(left_size - 1, -1, -1):
        # restart right_pos if it went over in a previous iteration
        if right_pos == right_size:
            right_pos = right_size - 1

        # find first position in right whose value is greater than left's
        if allow_exact_matches:
            while right_pos >= 0 and\
                right_values[right_pos] >= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        else:
            while right_pos >= 0 and\
                right_values[right_pos] > left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        right_pos += 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = right_values[found_right_pos] - left_values[left_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_nearest_int32_t_by_int64_t(
        ndarray[int32_t] left_values,
        ndarray[int32_t] right_values,
        ndarray[int64_t] left_by_values,
        ndarray[int64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_size, right_size, i
        ndarray[int64_t] left_indexer, right_indexer, bli, bri, fli, fri
        int32_t bdiff, fdiff

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    # search both forward and backward
    bli, bri =\
        asof_join_backward_int32_t_by_int64_t(left_values,
                                                        right_values,
                                                        left_by_values,
                                                        right_by_values,
                                                        allow_exact_matches,
                                                        tolerance)
    fli, fri =\
        asof_join_forward_int32_t_by_int64_t(left_values,
                                                       right_values,
                                                       left_by_values,
                                                       right_by_values,
                                                       allow_exact_matches,
                                                       tolerance)

    for i in range(len(bri)):
        # choose timestamp from right with smaller difference
        if bri[i] != -1 and fri[i] != -1:
            bdiff = left_values[bli[i]] - right_values[bri[i]]
            fdiff = right_values[fri[i]] - left_values[fli[i]]
            right_indexer[i] = bri[i] if bdiff <= fdiff else fri[i]
        else:
            right_indexer[i] = bri[i] if bri[i] != -1 else fri[i]
        left_indexer[i] = bli[i]

    return left_indexer, right_indexer


def asof_join_backward_int64_t_by_int64_t(
        ndarray[int64_t] left_values,
        ndarray[int64_t] right_values,
        ndarray[int64_t] left_by_values,
        ndarray[int64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        int64_t tolerance_ = 0
        int64_t diff = 0
        Int64HashTable hash_table
        int64_t by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = Int64HashTable(right_size)

    right_pos = 0
    for left_pos in range(left_size):
        # restart right_pos if it went negative in a previous iteration
        if right_pos < 0:
            right_pos = 0

        # find last position in right whose value is less than left's
        if allow_exact_matches:
            while right_pos < right_size and\
                right_values[right_pos] <= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        else:
            while right_pos < right_size and\
                right_values[right_pos] < left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        right_pos -= 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = left_values[left_pos] - right_values[found_right_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_forward_int64_t_by_int64_t(
        ndarray[int64_t] left_values,
        ndarray[int64_t] right_values,
        ndarray[int64_t] left_by_values,
        ndarray[int64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        int64_t tolerance_ = 0
        int64_t diff = 0
        Int64HashTable hash_table
        int64_t by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = Int64HashTable(right_size)

    right_pos = right_size - 1
    for left_pos in range(left_size - 1, -1, -1):
        # restart right_pos if it went over in a previous iteration
        if right_pos == right_size:
            right_pos = right_size - 1

        # find first position in right whose value is greater than left's
        if allow_exact_matches:
            while right_pos >= 0 and\
                right_values[right_pos] >= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        else:
            while right_pos >= 0 and\
                right_values[right_pos] > left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        right_pos += 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = right_values[found_right_pos] - left_values[left_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_nearest_int64_t_by_int64_t(
        ndarray[int64_t] left_values,
        ndarray[int64_t] right_values,
        ndarray[int64_t] left_by_values,
        ndarray[int64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_size, right_size, i
        ndarray[int64_t] left_indexer, right_indexer, bli, bri, fli, fri
        int64_t bdiff, fdiff

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    # search both forward and backward
    bli, bri =\
        asof_join_backward_int64_t_by_int64_t(left_values,
                                                        right_values,
                                                        left_by_values,
                                                        right_by_values,
                                                        allow_exact_matches,
                                                        tolerance)
    fli, fri =\
        asof_join_forward_int64_t_by_int64_t(left_values,
                                                       right_values,
                                                       left_by_values,
                                                       right_by_values,
                                                       allow_exact_matches,
                                                       tolerance)

    for i in range(len(bri)):
        # choose timestamp from right with smaller difference
        if bri[i] != -1 and fri[i] != -1:
            bdiff = left_values[bli[i]] - right_values[bri[i]]
            fdiff = right_values[fri[i]] - left_values[fli[i]]
            right_indexer[i] = bri[i] if bdiff <= fdiff else fri[i]
        else:
            right_indexer[i] = bri[i] if bri[i] != -1 else fri[i]
        left_indexer[i] = bli[i]

    return left_indexer, right_indexer


def asof_join_backward_float_by_int64_t(
        ndarray[float] left_values,
        ndarray[float] right_values,
        ndarray[int64_t] left_by_values,
        ndarray[int64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        float tolerance_ = 0
        float diff = 0
        Int64HashTable hash_table
        int64_t by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = Int64HashTable(right_size)

    right_pos = 0
    for left_pos in range(left_size):
        # restart right_pos if it went negative in a previous iteration
        if right_pos < 0:
            right_pos = 0

        # find last position in right whose value is less than left's
        if allow_exact_matches:
            while right_pos < right_size and\
                right_values[right_pos] <= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        else:
            while right_pos < right_size and\
                right_values[right_pos] < left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        right_pos -= 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = left_values[left_pos] - right_values[found_right_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_forward_float_by_int64_t(
        ndarray[float] left_values,
        ndarray[float] right_values,
        ndarray[int64_t] left_by_values,
        ndarray[int64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        float tolerance_ = 0
        float diff = 0
        Int64HashTable hash_table
        int64_t by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = Int64HashTable(right_size)

    right_pos = right_size - 1
    for left_pos in range(left_size - 1, -1, -1):
        # restart right_pos if it went over in a previous iteration
        if right_pos == right_size:
            right_pos = right_size - 1

        # find first position in right whose value is greater than left's
        if allow_exact_matches:
            while right_pos >= 0 and\
                right_values[right_pos] >= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        else:
            while right_pos >= 0 and\
                right_values[right_pos] > left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        right_pos += 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = right_values[found_right_pos] - left_values[left_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_nearest_float_by_int64_t(
        ndarray[float] left_values,
        ndarray[float] right_values,
        ndarray[int64_t] left_by_values,
        ndarray[int64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_size, right_size, i
        ndarray[int64_t] left_indexer, right_indexer, bli, bri, fli, fri
        float bdiff, fdiff

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    # search both forward and backward
    bli, bri =\
        asof_join_backward_float_by_int64_t(left_values,
                                                        right_values,
                                                        left_by_values,
                                                        right_by_values,
                                                        allow_exact_matches,
                                                        tolerance)
    fli, fri =\
        asof_join_forward_float_by_int64_t(left_values,
                                                       right_values,
                                                       left_by_values,
                                                       right_by_values,
                                                       allow_exact_matches,
                                                       tolerance)

    for i in range(len(bri)):
        # choose timestamp from right with smaller difference
        if bri[i] != -1 and fri[i] != -1:
            bdiff = left_values[bli[i]] - right_values[bri[i]]
            fdiff = right_values[fri[i]] - left_values[fli[i]]
            right_indexer[i] = bri[i] if bdiff <= fdiff else fri[i]
        else:
            right_indexer[i] = bri[i] if bri[i] != -1 else fri[i]
        left_indexer[i] = bli[i]

    return left_indexer, right_indexer


def asof_join_backward_double_by_int64_t(
        ndarray[double] left_values,
        ndarray[double] right_values,
        ndarray[int64_t] left_by_values,
        ndarray[int64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        double tolerance_ = 0
        double diff = 0
        Int64HashTable hash_table
        int64_t by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = Int64HashTable(right_size)

    right_pos = 0
    for left_pos in range(left_size):
        # restart right_pos if it went negative in a previous iteration
        if right_pos < 0:
            right_pos = 0

        # find last position in right whose value is less than left's
        if allow_exact_matches:
            while right_pos < right_size and\
                right_values[right_pos] <= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        else:
            while right_pos < right_size and\
                right_values[right_pos] < left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        right_pos -= 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = left_values[left_pos] - right_values[found_right_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_forward_double_by_int64_t(
        ndarray[double] left_values,
        ndarray[double] right_values,
        ndarray[int64_t] left_by_values,
        ndarray[int64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        double tolerance_ = 0
        double diff = 0
        Int64HashTable hash_table
        int64_t by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = Int64HashTable(right_size)

    right_pos = right_size - 1
    for left_pos in range(left_size - 1, -1, -1):
        # restart right_pos if it went over in a previous iteration
        if right_pos == right_size:
            right_pos = right_size - 1

        # find first position in right whose value is greater than left's
        if allow_exact_matches:
            while right_pos >= 0 and\
                right_values[right_pos] >= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        else:
            while right_pos >= 0 and\
                right_values[right_pos] > left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        right_pos += 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = right_values[found_right_pos] - left_values[left_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_nearest_double_by_int64_t(
        ndarray[double] left_values,
        ndarray[double] right_values,
        ndarray[int64_t] left_by_values,
        ndarray[int64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_size, right_size, i
        ndarray[int64_t] left_indexer, right_indexer, bli, bri, fli, fri
        double bdiff, fdiff

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    # search both forward and backward
    bli, bri =\
        asof_join_backward_double_by_int64_t(left_values,
                                                        right_values,
                                                        left_by_values,
                                                        right_by_values,
                                                        allow_exact_matches,
                                                        tolerance)
    fli, fri =\
        asof_join_forward_double_by_int64_t(left_values,
                                                       right_values,
                                                       left_by_values,
                                                       right_by_values,
                                                       allow_exact_matches,
                                                       tolerance)

    for i in range(len(bri)):
        # choose timestamp from right with smaller difference
        if bri[i] != -1 and fri[i] != -1:
            bdiff = left_values[bli[i]] - right_values[bri[i]]
            fdiff = right_values[fri[i]] - left_values[fli[i]]
            right_indexer[i] = bri[i] if bdiff <= fdiff else fri[i]
        else:
            right_indexer[i] = bri[i] if bri[i] != -1 else fri[i]
        left_indexer[i] = bli[i]

    return left_indexer, right_indexer


def asof_join_backward_uint8_t_by_uint64_t(
        ndarray[uint8_t] left_values,
        ndarray[uint8_t] right_values,
        ndarray[uint64_t] left_by_values,
        ndarray[uint64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        uint8_t tolerance_ = 0
        uint8_t diff = 0
        UInt64HashTable hash_table
        uint64_t by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = UInt64HashTable(right_size)

    right_pos = 0
    for left_pos in range(left_size):
        # restart right_pos if it went negative in a previous iteration
        if right_pos < 0:
            right_pos = 0

        # find last position in right whose value is less than left's
        if allow_exact_matches:
            while right_pos < right_size and\
                right_values[right_pos] <= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        else:
            while right_pos < right_size and\
                right_values[right_pos] < left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        right_pos -= 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = left_values[left_pos] - right_values[found_right_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_forward_uint8_t_by_uint64_t(
        ndarray[uint8_t] left_values,
        ndarray[uint8_t] right_values,
        ndarray[uint64_t] left_by_values,
        ndarray[uint64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        uint8_t tolerance_ = 0
        uint8_t diff = 0
        UInt64HashTable hash_table
        uint64_t by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = UInt64HashTable(right_size)

    right_pos = right_size - 1
    for left_pos in range(left_size - 1, -1, -1):
        # restart right_pos if it went over in a previous iteration
        if right_pos == right_size:
            right_pos = right_size - 1

        # find first position in right whose value is greater than left's
        if allow_exact_matches:
            while right_pos >= 0 and\
                right_values[right_pos] >= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        else:
            while right_pos >= 0 and\
                right_values[right_pos] > left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        right_pos += 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = right_values[found_right_pos] - left_values[left_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_nearest_uint8_t_by_uint64_t(
        ndarray[uint8_t] left_values,
        ndarray[uint8_t] right_values,
        ndarray[uint64_t] left_by_values,
        ndarray[uint64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_size, right_size, i
        ndarray[int64_t] left_indexer, right_indexer, bli, bri, fli, fri
        uint8_t bdiff, fdiff

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    # search both forward and backward
    bli, bri =\
        asof_join_backward_uint8_t_by_uint64_t(left_values,
                                                        right_values,
                                                        left_by_values,
                                                        right_by_values,
                                                        allow_exact_matches,
                                                        tolerance)
    fli, fri =\
        asof_join_forward_uint8_t_by_uint64_t(left_values,
                                                       right_values,
                                                       left_by_values,
                                                       right_by_values,
                                                       allow_exact_matches,
                                                       tolerance)

    for i in range(len(bri)):
        # choose timestamp from right with smaller difference
        if bri[i] != -1 and fri[i] != -1:
            bdiff = left_values[bli[i]] - right_values[bri[i]]
            fdiff = right_values[fri[i]] - left_values[fli[i]]
            right_indexer[i] = bri[i] if bdiff <= fdiff else fri[i]
        else:
            right_indexer[i] = bri[i] if bri[i] != -1 else fri[i]
        left_indexer[i] = bli[i]

    return left_indexer, right_indexer


def asof_join_backward_uint16_t_by_uint64_t(
        ndarray[uint16_t] left_values,
        ndarray[uint16_t] right_values,
        ndarray[uint64_t] left_by_values,
        ndarray[uint64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        uint16_t tolerance_ = 0
        uint16_t diff = 0
        UInt64HashTable hash_table
        uint64_t by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = UInt64HashTable(right_size)

    right_pos = 0
    for left_pos in range(left_size):
        # restart right_pos if it went negative in a previous iteration
        if right_pos < 0:
            right_pos = 0

        # find last position in right whose value is less than left's
        if allow_exact_matches:
            while right_pos < right_size and\
                right_values[right_pos] <= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        else:
            while right_pos < right_size and\
                right_values[right_pos] < left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        right_pos -= 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = left_values[left_pos] - right_values[found_right_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_forward_uint16_t_by_uint64_t(
        ndarray[uint16_t] left_values,
        ndarray[uint16_t] right_values,
        ndarray[uint64_t] left_by_values,
        ndarray[uint64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        uint16_t tolerance_ = 0
        uint16_t diff = 0
        UInt64HashTable hash_table
        uint64_t by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = UInt64HashTable(right_size)

    right_pos = right_size - 1
    for left_pos in range(left_size - 1, -1, -1):
        # restart right_pos if it went over in a previous iteration
        if right_pos == right_size:
            right_pos = right_size - 1

        # find first position in right whose value is greater than left's
        if allow_exact_matches:
            while right_pos >= 0 and\
                right_values[right_pos] >= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        else:
            while right_pos >= 0 and\
                right_values[right_pos] > left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        right_pos += 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = right_values[found_right_pos] - left_values[left_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_nearest_uint16_t_by_uint64_t(
        ndarray[uint16_t] left_values,
        ndarray[uint16_t] right_values,
        ndarray[uint64_t] left_by_values,
        ndarray[uint64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_size, right_size, i
        ndarray[int64_t] left_indexer, right_indexer, bli, bri, fli, fri
        uint16_t bdiff, fdiff

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    # search both forward and backward
    bli, bri =\
        asof_join_backward_uint16_t_by_uint64_t(left_values,
                                                        right_values,
                                                        left_by_values,
                                                        right_by_values,
                                                        allow_exact_matches,
                                                        tolerance)
    fli, fri =\
        asof_join_forward_uint16_t_by_uint64_t(left_values,
                                                       right_values,
                                                       left_by_values,
                                                       right_by_values,
                                                       allow_exact_matches,
                                                       tolerance)

    for i in range(len(bri)):
        # choose timestamp from right with smaller difference
        if bri[i] != -1 and fri[i] != -1:
            bdiff = left_values[bli[i]] - right_values[bri[i]]
            fdiff = right_values[fri[i]] - left_values[fli[i]]
            right_indexer[i] = bri[i] if bdiff <= fdiff else fri[i]
        else:
            right_indexer[i] = bri[i] if bri[i] != -1 else fri[i]
        left_indexer[i] = bli[i]

    return left_indexer, right_indexer


def asof_join_backward_uint32_t_by_uint64_t(
        ndarray[uint32_t] left_values,
        ndarray[uint32_t] right_values,
        ndarray[uint64_t] left_by_values,
        ndarray[uint64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        uint32_t tolerance_ = 0
        uint32_t diff = 0
        UInt64HashTable hash_table
        uint64_t by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = UInt64HashTable(right_size)

    right_pos = 0
    for left_pos in range(left_size):
        # restart right_pos if it went negative in a previous iteration
        if right_pos < 0:
            right_pos = 0

        # find last position in right whose value is less than left's
        if allow_exact_matches:
            while right_pos < right_size and\
                right_values[right_pos] <= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        else:
            while right_pos < right_size and\
                right_values[right_pos] < left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        right_pos -= 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = left_values[left_pos] - right_values[found_right_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_forward_uint32_t_by_uint64_t(
        ndarray[uint32_t] left_values,
        ndarray[uint32_t] right_values,
        ndarray[uint64_t] left_by_values,
        ndarray[uint64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        uint32_t tolerance_ = 0
        uint32_t diff = 0
        UInt64HashTable hash_table
        uint64_t by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = UInt64HashTable(right_size)

    right_pos = right_size - 1
    for left_pos in range(left_size - 1, -1, -1):
        # restart right_pos if it went over in a previous iteration
        if right_pos == right_size:
            right_pos = right_size - 1

        # find first position in right whose value is greater than left's
        if allow_exact_matches:
            while right_pos >= 0 and\
                right_values[right_pos] >= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        else:
            while right_pos >= 0 and\
                right_values[right_pos] > left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        right_pos += 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = right_values[found_right_pos] - left_values[left_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_nearest_uint32_t_by_uint64_t(
        ndarray[uint32_t] left_values,
        ndarray[uint32_t] right_values,
        ndarray[uint64_t] left_by_values,
        ndarray[uint64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_size, right_size, i
        ndarray[int64_t] left_indexer, right_indexer, bli, bri, fli, fri
        uint32_t bdiff, fdiff

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    # search both forward and backward
    bli, bri =\
        asof_join_backward_uint32_t_by_uint64_t(left_values,
                                                        right_values,
                                                        left_by_values,
                                                        right_by_values,
                                                        allow_exact_matches,
                                                        tolerance)
    fli, fri =\
        asof_join_forward_uint32_t_by_uint64_t(left_values,
                                                       right_values,
                                                       left_by_values,
                                                       right_by_values,
                                                       allow_exact_matches,
                                                       tolerance)

    for i in range(len(bri)):
        # choose timestamp from right with smaller difference
        if bri[i] != -1 and fri[i] != -1:
            bdiff = left_values[bli[i]] - right_values[bri[i]]
            fdiff = right_values[fri[i]] - left_values[fli[i]]
            right_indexer[i] = bri[i] if bdiff <= fdiff else fri[i]
        else:
            right_indexer[i] = bri[i] if bri[i] != -1 else fri[i]
        left_indexer[i] = bli[i]

    return left_indexer, right_indexer


def asof_join_backward_uint64_t_by_uint64_t(
        ndarray[uint64_t] left_values,
        ndarray[uint64_t] right_values,
        ndarray[uint64_t] left_by_values,
        ndarray[uint64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        uint64_t tolerance_ = 0
        uint64_t diff = 0
        UInt64HashTable hash_table
        uint64_t by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = UInt64HashTable(right_size)

    right_pos = 0
    for left_pos in range(left_size):
        # restart right_pos if it went negative in a previous iteration
        if right_pos < 0:
            right_pos = 0

        # find last position in right whose value is less than left's
        if allow_exact_matches:
            while right_pos < right_size and\
                right_values[right_pos] <= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        else:
            while right_pos < right_size and\
                right_values[right_pos] < left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        right_pos -= 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = left_values[left_pos] - right_values[found_right_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_forward_uint64_t_by_uint64_t(
        ndarray[uint64_t] left_values,
        ndarray[uint64_t] right_values,
        ndarray[uint64_t] left_by_values,
        ndarray[uint64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        uint64_t tolerance_ = 0
        uint64_t diff = 0
        UInt64HashTable hash_table
        uint64_t by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = UInt64HashTable(right_size)

    right_pos = right_size - 1
    for left_pos in range(left_size - 1, -1, -1):
        # restart right_pos if it went over in a previous iteration
        if right_pos == right_size:
            right_pos = right_size - 1

        # find first position in right whose value is greater than left's
        if allow_exact_matches:
            while right_pos >= 0 and\
                right_values[right_pos] >= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        else:
            while right_pos >= 0 and\
                right_values[right_pos] > left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        right_pos += 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = right_values[found_right_pos] - left_values[left_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_nearest_uint64_t_by_uint64_t(
        ndarray[uint64_t] left_values,
        ndarray[uint64_t] right_values,
        ndarray[uint64_t] left_by_values,
        ndarray[uint64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_size, right_size, i
        ndarray[int64_t] left_indexer, right_indexer, bli, bri, fli, fri
        uint64_t bdiff, fdiff

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    # search both forward and backward
    bli, bri =\
        asof_join_backward_uint64_t_by_uint64_t(left_values,
                                                        right_values,
                                                        left_by_values,
                                                        right_by_values,
                                                        allow_exact_matches,
                                                        tolerance)
    fli, fri =\
        asof_join_forward_uint64_t_by_uint64_t(left_values,
                                                       right_values,
                                                       left_by_values,
                                                       right_by_values,
                                                       allow_exact_matches,
                                                       tolerance)

    for i in range(len(bri)):
        # choose timestamp from right with smaller difference
        if bri[i] != -1 and fri[i] != -1:
            bdiff = left_values[bli[i]] - right_values[bri[i]]
            fdiff = right_values[fri[i]] - left_values[fli[i]]
            right_indexer[i] = bri[i] if bdiff <= fdiff else fri[i]
        else:
            right_indexer[i] = bri[i] if bri[i] != -1 else fri[i]
        left_indexer[i] = bli[i]

    return left_indexer, right_indexer


def asof_join_backward_int8_t_by_uint64_t(
        ndarray[int8_t] left_values,
        ndarray[int8_t] right_values,
        ndarray[uint64_t] left_by_values,
        ndarray[uint64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        int8_t tolerance_ = 0
        int8_t diff = 0
        UInt64HashTable hash_table
        uint64_t by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = UInt64HashTable(right_size)

    right_pos = 0
    for left_pos in range(left_size):
        # restart right_pos if it went negative in a previous iteration
        if right_pos < 0:
            right_pos = 0

        # find last position in right whose value is less than left's
        if allow_exact_matches:
            while right_pos < right_size and\
                right_values[right_pos] <= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        else:
            while right_pos < right_size and\
                right_values[right_pos] < left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        right_pos -= 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = left_values[left_pos] - right_values[found_right_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_forward_int8_t_by_uint64_t(
        ndarray[int8_t] left_values,
        ndarray[int8_t] right_values,
        ndarray[uint64_t] left_by_values,
        ndarray[uint64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        int8_t tolerance_ = 0
        int8_t diff = 0
        UInt64HashTable hash_table
        uint64_t by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = UInt64HashTable(right_size)

    right_pos = right_size - 1
    for left_pos in range(left_size - 1, -1, -1):
        # restart right_pos if it went over in a previous iteration
        if right_pos == right_size:
            right_pos = right_size - 1

        # find first position in right whose value is greater than left's
        if allow_exact_matches:
            while right_pos >= 0 and\
                right_values[right_pos] >= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        else:
            while right_pos >= 0 and\
                right_values[right_pos] > left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        right_pos += 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = right_values[found_right_pos] - left_values[left_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_nearest_int8_t_by_uint64_t(
        ndarray[int8_t] left_values,
        ndarray[int8_t] right_values,
        ndarray[uint64_t] left_by_values,
        ndarray[uint64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_size, right_size, i
        ndarray[int64_t] left_indexer, right_indexer, bli, bri, fli, fri
        int8_t bdiff, fdiff

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    # search both forward and backward
    bli, bri =\
        asof_join_backward_int8_t_by_uint64_t(left_values,
                                                        right_values,
                                                        left_by_values,
                                                        right_by_values,
                                                        allow_exact_matches,
                                                        tolerance)
    fli, fri =\
        asof_join_forward_int8_t_by_uint64_t(left_values,
                                                       right_values,
                                                       left_by_values,
                                                       right_by_values,
                                                       allow_exact_matches,
                                                       tolerance)

    for i in range(len(bri)):
        # choose timestamp from right with smaller difference
        if bri[i] != -1 and fri[i] != -1:
            bdiff = left_values[bli[i]] - right_values[bri[i]]
            fdiff = right_values[fri[i]] - left_values[fli[i]]
            right_indexer[i] = bri[i] if bdiff <= fdiff else fri[i]
        else:
            right_indexer[i] = bri[i] if bri[i] != -1 else fri[i]
        left_indexer[i] = bli[i]

    return left_indexer, right_indexer


def asof_join_backward_int16_t_by_uint64_t(
        ndarray[int16_t] left_values,
        ndarray[int16_t] right_values,
        ndarray[uint64_t] left_by_values,
        ndarray[uint64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        int16_t tolerance_ = 0
        int16_t diff = 0
        UInt64HashTable hash_table
        uint64_t by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = UInt64HashTable(right_size)

    right_pos = 0
    for left_pos in range(left_size):
        # restart right_pos if it went negative in a previous iteration
        if right_pos < 0:
            right_pos = 0

        # find last position in right whose value is less than left's
        if allow_exact_matches:
            while right_pos < right_size and\
                right_values[right_pos] <= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        else:
            while right_pos < right_size and\
                right_values[right_pos] < left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        right_pos -= 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = left_values[left_pos] - right_values[found_right_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_forward_int16_t_by_uint64_t(
        ndarray[int16_t] left_values,
        ndarray[int16_t] right_values,
        ndarray[uint64_t] left_by_values,
        ndarray[uint64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        int16_t tolerance_ = 0
        int16_t diff = 0
        UInt64HashTable hash_table
        uint64_t by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = UInt64HashTable(right_size)

    right_pos = right_size - 1
    for left_pos in range(left_size - 1, -1, -1):
        # restart right_pos if it went over in a previous iteration
        if right_pos == right_size:
            right_pos = right_size - 1

        # find first position in right whose value is greater than left's
        if allow_exact_matches:
            while right_pos >= 0 and\
                right_values[right_pos] >= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        else:
            while right_pos >= 0 and\
                right_values[right_pos] > left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        right_pos += 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = right_values[found_right_pos] - left_values[left_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_nearest_int16_t_by_uint64_t(
        ndarray[int16_t] left_values,
        ndarray[int16_t] right_values,
        ndarray[uint64_t] left_by_values,
        ndarray[uint64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_size, right_size, i
        ndarray[int64_t] left_indexer, right_indexer, bli, bri, fli, fri
        int16_t bdiff, fdiff

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    # search both forward and backward
    bli, bri =\
        asof_join_backward_int16_t_by_uint64_t(left_values,
                                                        right_values,
                                                        left_by_values,
                                                        right_by_values,
                                                        allow_exact_matches,
                                                        tolerance)
    fli, fri =\
        asof_join_forward_int16_t_by_uint64_t(left_values,
                                                       right_values,
                                                       left_by_values,
                                                       right_by_values,
                                                       allow_exact_matches,
                                                       tolerance)

    for i in range(len(bri)):
        # choose timestamp from right with smaller difference
        if bri[i] != -1 and fri[i] != -1:
            bdiff = left_values[bli[i]] - right_values[bri[i]]
            fdiff = right_values[fri[i]] - left_values[fli[i]]
            right_indexer[i] = bri[i] if bdiff <= fdiff else fri[i]
        else:
            right_indexer[i] = bri[i] if bri[i] != -1 else fri[i]
        left_indexer[i] = bli[i]

    return left_indexer, right_indexer


def asof_join_backward_int32_t_by_uint64_t(
        ndarray[int32_t] left_values,
        ndarray[int32_t] right_values,
        ndarray[uint64_t] left_by_values,
        ndarray[uint64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        int32_t tolerance_ = 0
        int32_t diff = 0
        UInt64HashTable hash_table
        uint64_t by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = UInt64HashTable(right_size)

    right_pos = 0
    for left_pos in range(left_size):
        # restart right_pos if it went negative in a previous iteration
        if right_pos < 0:
            right_pos = 0

        # find last position in right whose value is less than left's
        if allow_exact_matches:
            while right_pos < right_size and\
                right_values[right_pos] <= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        else:
            while right_pos < right_size and\
                right_values[right_pos] < left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        right_pos -= 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = left_values[left_pos] - right_values[found_right_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_forward_int32_t_by_uint64_t(
        ndarray[int32_t] left_values,
        ndarray[int32_t] right_values,
        ndarray[uint64_t] left_by_values,
        ndarray[uint64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        int32_t tolerance_ = 0
        int32_t diff = 0
        UInt64HashTable hash_table
        uint64_t by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = UInt64HashTable(right_size)

    right_pos = right_size - 1
    for left_pos in range(left_size - 1, -1, -1):
        # restart right_pos if it went over in a previous iteration
        if right_pos == right_size:
            right_pos = right_size - 1

        # find first position in right whose value is greater than left's
        if allow_exact_matches:
            while right_pos >= 0 and\
                right_values[right_pos] >= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        else:
            while right_pos >= 0 and\
                right_values[right_pos] > left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        right_pos += 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = right_values[found_right_pos] - left_values[left_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_nearest_int32_t_by_uint64_t(
        ndarray[int32_t] left_values,
        ndarray[int32_t] right_values,
        ndarray[uint64_t] left_by_values,
        ndarray[uint64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_size, right_size, i
        ndarray[int64_t] left_indexer, right_indexer, bli, bri, fli, fri
        int32_t bdiff, fdiff

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    # search both forward and backward
    bli, bri =\
        asof_join_backward_int32_t_by_uint64_t(left_values,
                                                        right_values,
                                                        left_by_values,
                                                        right_by_values,
                                                        allow_exact_matches,
                                                        tolerance)
    fli, fri =\
        asof_join_forward_int32_t_by_uint64_t(left_values,
                                                       right_values,
                                                       left_by_values,
                                                       right_by_values,
                                                       allow_exact_matches,
                                                       tolerance)

    for i in range(len(bri)):
        # choose timestamp from right with smaller difference
        if bri[i] != -1 and fri[i] != -1:
            bdiff = left_values[bli[i]] - right_values[bri[i]]
            fdiff = right_values[fri[i]] - left_values[fli[i]]
            right_indexer[i] = bri[i] if bdiff <= fdiff else fri[i]
        else:
            right_indexer[i] = bri[i] if bri[i] != -1 else fri[i]
        left_indexer[i] = bli[i]

    return left_indexer, right_indexer


def asof_join_backward_int64_t_by_uint64_t(
        ndarray[int64_t] left_values,
        ndarray[int64_t] right_values,
        ndarray[uint64_t] left_by_values,
        ndarray[uint64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        int64_t tolerance_ = 0
        int64_t diff = 0
        UInt64HashTable hash_table
        uint64_t by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = UInt64HashTable(right_size)

    right_pos = 0
    for left_pos in range(left_size):
        # restart right_pos if it went negative in a previous iteration
        if right_pos < 0:
            right_pos = 0

        # find last position in right whose value is less than left's
        if allow_exact_matches:
            while right_pos < right_size and\
                right_values[right_pos] <= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        else:
            while right_pos < right_size and\
                right_values[right_pos] < left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        right_pos -= 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = left_values[left_pos] - right_values[found_right_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_forward_int64_t_by_uint64_t(
        ndarray[int64_t] left_values,
        ndarray[int64_t] right_values,
        ndarray[uint64_t] left_by_values,
        ndarray[uint64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        int64_t tolerance_ = 0
        int64_t diff = 0
        UInt64HashTable hash_table
        uint64_t by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = UInt64HashTable(right_size)

    right_pos = right_size - 1
    for left_pos in range(left_size - 1, -1, -1):
        # restart right_pos if it went over in a previous iteration
        if right_pos == right_size:
            right_pos = right_size - 1

        # find first position in right whose value is greater than left's
        if allow_exact_matches:
            while right_pos >= 0 and\
                right_values[right_pos] >= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        else:
            while right_pos >= 0 and\
                right_values[right_pos] > left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        right_pos += 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = right_values[found_right_pos] - left_values[left_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_nearest_int64_t_by_uint64_t(
        ndarray[int64_t] left_values,
        ndarray[int64_t] right_values,
        ndarray[uint64_t] left_by_values,
        ndarray[uint64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_size, right_size, i
        ndarray[int64_t] left_indexer, right_indexer, bli, bri, fli, fri
        int64_t bdiff, fdiff

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    # search both forward and backward
    bli, bri =\
        asof_join_backward_int64_t_by_uint64_t(left_values,
                                                        right_values,
                                                        left_by_values,
                                                        right_by_values,
                                                        allow_exact_matches,
                                                        tolerance)
    fli, fri =\
        asof_join_forward_int64_t_by_uint64_t(left_values,
                                                       right_values,
                                                       left_by_values,
                                                       right_by_values,
                                                       allow_exact_matches,
                                                       tolerance)

    for i in range(len(bri)):
        # choose timestamp from right with smaller difference
        if bri[i] != -1 and fri[i] != -1:
            bdiff = left_values[bli[i]] - right_values[bri[i]]
            fdiff = right_values[fri[i]] - left_values[fli[i]]
            right_indexer[i] = bri[i] if bdiff <= fdiff else fri[i]
        else:
            right_indexer[i] = bri[i] if bri[i] != -1 else fri[i]
        left_indexer[i] = bli[i]

    return left_indexer, right_indexer


def asof_join_backward_float_by_uint64_t(
        ndarray[float] left_values,
        ndarray[float] right_values,
        ndarray[uint64_t] left_by_values,
        ndarray[uint64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        float tolerance_ = 0
        float diff = 0
        UInt64HashTable hash_table
        uint64_t by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = UInt64HashTable(right_size)

    right_pos = 0
    for left_pos in range(left_size):
        # restart right_pos if it went negative in a previous iteration
        if right_pos < 0:
            right_pos = 0

        # find last position in right whose value is less than left's
        if allow_exact_matches:
            while right_pos < right_size and\
                right_values[right_pos] <= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        else:
            while right_pos < right_size and\
                right_values[right_pos] < left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        right_pos -= 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = left_values[left_pos] - right_values[found_right_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_forward_float_by_uint64_t(
        ndarray[float] left_values,
        ndarray[float] right_values,
        ndarray[uint64_t] left_by_values,
        ndarray[uint64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        float tolerance_ = 0
        float diff = 0
        UInt64HashTable hash_table
        uint64_t by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = UInt64HashTable(right_size)

    right_pos = right_size - 1
    for left_pos in range(left_size - 1, -1, -1):
        # restart right_pos if it went over in a previous iteration
        if right_pos == right_size:
            right_pos = right_size - 1

        # find first position in right whose value is greater than left's
        if allow_exact_matches:
            while right_pos >= 0 and\
                right_values[right_pos] >= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        else:
            while right_pos >= 0 and\
                right_values[right_pos] > left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        right_pos += 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = right_values[found_right_pos] - left_values[left_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_nearest_float_by_uint64_t(
        ndarray[float] left_values,
        ndarray[float] right_values,
        ndarray[uint64_t] left_by_values,
        ndarray[uint64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_size, right_size, i
        ndarray[int64_t] left_indexer, right_indexer, bli, bri, fli, fri
        float bdiff, fdiff

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    # search both forward and backward
    bli, bri =\
        asof_join_backward_float_by_uint64_t(left_values,
                                                        right_values,
                                                        left_by_values,
                                                        right_by_values,
                                                        allow_exact_matches,
                                                        tolerance)
    fli, fri =\
        asof_join_forward_float_by_uint64_t(left_values,
                                                       right_values,
                                                       left_by_values,
                                                       right_by_values,
                                                       allow_exact_matches,
                                                       tolerance)

    for i in range(len(bri)):
        # choose timestamp from right with smaller difference
        if bri[i] != -1 and fri[i] != -1:
            bdiff = left_values[bli[i]] - right_values[bri[i]]
            fdiff = right_values[fri[i]] - left_values[fli[i]]
            right_indexer[i] = bri[i] if bdiff <= fdiff else fri[i]
        else:
            right_indexer[i] = bri[i] if bri[i] != -1 else fri[i]
        left_indexer[i] = bli[i]

    return left_indexer, right_indexer


def asof_join_backward_double_by_uint64_t(
        ndarray[double] left_values,
        ndarray[double] right_values,
        ndarray[uint64_t] left_by_values,
        ndarray[uint64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        double tolerance_ = 0
        double diff = 0
        UInt64HashTable hash_table
        uint64_t by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = UInt64HashTable(right_size)

    right_pos = 0
    for left_pos in range(left_size):
        # restart right_pos if it went negative in a previous iteration
        if right_pos < 0:
            right_pos = 0

        # find last position in right whose value is less than left's
        if allow_exact_matches:
            while right_pos < right_size and\
                right_values[right_pos] <= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        else:
            while right_pos < right_size and\
                right_values[right_pos] < left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos += 1
        right_pos -= 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = left_values[left_pos] - right_values[found_right_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_forward_double_by_uint64_t(
        ndarray[double] left_values,
        ndarray[double] right_values,
        ndarray[uint64_t] left_by_values,
        ndarray[uint64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size, found_right_pos
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        double tolerance_ = 0
        double diff = 0
        UInt64HashTable hash_table
        uint64_t by_value

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    hash_table = UInt64HashTable(right_size)

    right_pos = right_size - 1
    for left_pos in range(left_size - 1, -1, -1):
        # restart right_pos if it went over in a previous iteration
        if right_pos == right_size:
            right_pos = right_size - 1

        # find first position in right whose value is greater than left's
        if allow_exact_matches:
            while right_pos >= 0 and\
                right_values[right_pos] >= left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        else:
            while right_pos >= 0 and\
                right_values[right_pos] > left_values[left_pos]:
                hash_table.set_item(right_by_values[right_pos], right_pos)
                right_pos -= 1
        right_pos += 1

        # save positions as the desired index
        by_value = left_by_values[left_pos]
        found_right_pos = hash_table.get_item(by_value)\
                          if by_value in hash_table else -1
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = found_right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and found_right_pos != -1:
            diff = right_values[found_right_pos] - left_values[left_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_nearest_double_by_uint64_t(
        ndarray[double] left_values,
        ndarray[double] right_values,
        ndarray[uint64_t] left_by_values,
        ndarray[uint64_t] right_by_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_size, right_size, i
        ndarray[int64_t] left_indexer, right_indexer, bli, bri, fli, fri
        double bdiff, fdiff

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    # search both forward and backward
    bli, bri =\
        asof_join_backward_double_by_uint64_t(left_values,
                                                        right_values,
                                                        left_by_values,
                                                        right_by_values,
                                                        allow_exact_matches,
                                                        tolerance)
    fli, fri =\
        asof_join_forward_double_by_uint64_t(left_values,
                                                       right_values,
                                                       left_by_values,
                                                       right_by_values,
                                                       allow_exact_matches,
                                                       tolerance)

    for i in range(len(bri)):
        # choose timestamp from right with smaller difference
        if bri[i] != -1 and fri[i] != -1:
            bdiff = left_values[bli[i]] - right_values[bri[i]]
            fdiff = right_values[fri[i]] - left_values[fli[i]]
            right_indexer[i] = bri[i] if bdiff <= fdiff else fri[i]
        else:
            right_indexer[i] = bri[i] if bri[i] != -1 else fri[i]
        left_indexer[i] = bli[i]

    return left_indexer, right_indexer


#----------------------------------------------------------------------
# asof_join
#----------------------------------------------------------------------


def asof_join_backward_uint8_t(
        ndarray[uint8_t] left_values,
        ndarray[uint8_t] right_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        uint8_t tolerance_ = 0
        uint8_t diff = 0

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    right_pos = 0
    for left_pos in range(left_size):
        # restart right_pos if it went negative in a previous iteration
        if right_pos < 0:
            right_pos = 0

        # find last position in right whose value is less than left's
        if allow_exact_matches:
            while right_pos < right_size and\
                right_values[right_pos] <= left_values[left_pos]:
                right_pos += 1
        else:
            while right_pos < right_size and\
                right_values[right_pos] < left_values[left_pos]:
                right_pos += 1
        right_pos -= 1

        # save positions as the desired index
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and right_pos != -1:
            diff = left_values[left_pos] - right_values[right_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_forward_uint8_t(
        ndarray[uint8_t] left_values,
        ndarray[uint8_t] right_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        uint8_t tolerance_ = 0
        uint8_t diff = 0

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    right_pos = right_size - 1
    for left_pos in range(left_size - 1, -1, -1):
        # restart right_pos if it went over in a previous iteration
        if right_pos == right_size:
            right_pos = right_size - 1

        # find first position in right whose value is greater than left's
        if allow_exact_matches:
            while right_pos >= 0 and\
                right_values[right_pos] >= left_values[left_pos]:
                right_pos -= 1
        else:
            while right_pos >= 0 and\
                right_values[right_pos] > left_values[left_pos]:
                right_pos -= 1
        right_pos += 1

        # save positions as the desired index
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = right_pos\
                                  if right_pos != right_size else -1

        # if needed, verify that tolerance is met
        if has_tolerance and right_pos != right_size:
            diff = right_values[right_pos] - left_values[left_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_nearest_uint8_t(
        ndarray[uint8_t] left_values,
        ndarray[uint8_t] right_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_size, right_size, i
        ndarray[int64_t] left_indexer, right_indexer, bli, bri, fli, fri
        uint8_t bdiff, fdiff

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    # search both forward and backward
    bli, bri = asof_join_backward_uint8_t(left_values, right_values,
                                               allow_exact_matches, tolerance)
    fli, fri = asof_join_forward_uint8_t(left_values, right_values,
                                              allow_exact_matches, tolerance)

    for i in range(len(bri)):
        # choose timestamp from right with smaller difference
        if bri[i] != -1 and fri[i] != -1:
            bdiff = left_values[bli[i]] - right_values[bri[i]]
            fdiff = right_values[fri[i]] - left_values[fli[i]]
            right_indexer[i] = bri[i] if bdiff <= fdiff else fri[i]
        else:
            right_indexer[i] = bri[i] if bri[i] != -1 else fri[i]
        left_indexer[i] = bli[i]

    return left_indexer, right_indexer


def asof_join_backward_uint16_t(
        ndarray[uint16_t] left_values,
        ndarray[uint16_t] right_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        uint16_t tolerance_ = 0
        uint16_t diff = 0

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    right_pos = 0
    for left_pos in range(left_size):
        # restart right_pos if it went negative in a previous iteration
        if right_pos < 0:
            right_pos = 0

        # find last position in right whose value is less than left's
        if allow_exact_matches:
            while right_pos < right_size and\
                right_values[right_pos] <= left_values[left_pos]:
                right_pos += 1
        else:
            while right_pos < right_size and\
                right_values[right_pos] < left_values[left_pos]:
                right_pos += 1
        right_pos -= 1

        # save positions as the desired index
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and right_pos != -1:
            diff = left_values[left_pos] - right_values[right_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_forward_uint16_t(
        ndarray[uint16_t] left_values,
        ndarray[uint16_t] right_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        uint16_t tolerance_ = 0
        uint16_t diff = 0

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    right_pos = right_size - 1
    for left_pos in range(left_size - 1, -1, -1):
        # restart right_pos if it went over in a previous iteration
        if right_pos == right_size:
            right_pos = right_size - 1

        # find first position in right whose value is greater than left's
        if allow_exact_matches:
            while right_pos >= 0 and\
                right_values[right_pos] >= left_values[left_pos]:
                right_pos -= 1
        else:
            while right_pos >= 0 and\
                right_values[right_pos] > left_values[left_pos]:
                right_pos -= 1
        right_pos += 1

        # save positions as the desired index
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = right_pos\
                                  if right_pos != right_size else -1

        # if needed, verify that tolerance is met
        if has_tolerance and right_pos != right_size:
            diff = right_values[right_pos] - left_values[left_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_nearest_uint16_t(
        ndarray[uint16_t] left_values,
        ndarray[uint16_t] right_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_size, right_size, i
        ndarray[int64_t] left_indexer, right_indexer, bli, bri, fli, fri
        uint16_t bdiff, fdiff

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    # search both forward and backward
    bli, bri = asof_join_backward_uint16_t(left_values, right_values,
                                               allow_exact_matches, tolerance)
    fli, fri = asof_join_forward_uint16_t(left_values, right_values,
                                              allow_exact_matches, tolerance)

    for i in range(len(bri)):
        # choose timestamp from right with smaller difference
        if bri[i] != -1 and fri[i] != -1:
            bdiff = left_values[bli[i]] - right_values[bri[i]]
            fdiff = right_values[fri[i]] - left_values[fli[i]]
            right_indexer[i] = bri[i] if bdiff <= fdiff else fri[i]
        else:
            right_indexer[i] = bri[i] if bri[i] != -1 else fri[i]
        left_indexer[i] = bli[i]

    return left_indexer, right_indexer


def asof_join_backward_uint32_t(
        ndarray[uint32_t] left_values,
        ndarray[uint32_t] right_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        uint32_t tolerance_ = 0
        uint32_t diff = 0

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    right_pos = 0
    for left_pos in range(left_size):
        # restart right_pos if it went negative in a previous iteration
        if right_pos < 0:
            right_pos = 0

        # find last position in right whose value is less than left's
        if allow_exact_matches:
            while right_pos < right_size and\
                right_values[right_pos] <= left_values[left_pos]:
                right_pos += 1
        else:
            while right_pos < right_size and\
                right_values[right_pos] < left_values[left_pos]:
                right_pos += 1
        right_pos -= 1

        # save positions as the desired index
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and right_pos != -1:
            diff = left_values[left_pos] - right_values[right_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_forward_uint32_t(
        ndarray[uint32_t] left_values,
        ndarray[uint32_t] right_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        uint32_t tolerance_ = 0
        uint32_t diff = 0

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    right_pos = right_size - 1
    for left_pos in range(left_size - 1, -1, -1):
        # restart right_pos if it went over in a previous iteration
        if right_pos == right_size:
            right_pos = right_size - 1

        # find first position in right whose value is greater than left's
        if allow_exact_matches:
            while right_pos >= 0 and\
                right_values[right_pos] >= left_values[left_pos]:
                right_pos -= 1
        else:
            while right_pos >= 0 and\
                right_values[right_pos] > left_values[left_pos]:
                right_pos -= 1
        right_pos += 1

        # save positions as the desired index
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = right_pos\
                                  if right_pos != right_size else -1

        # if needed, verify that tolerance is met
        if has_tolerance and right_pos != right_size:
            diff = right_values[right_pos] - left_values[left_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_nearest_uint32_t(
        ndarray[uint32_t] left_values,
        ndarray[uint32_t] right_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_size, right_size, i
        ndarray[int64_t] left_indexer, right_indexer, bli, bri, fli, fri
        uint32_t bdiff, fdiff

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    # search both forward and backward
    bli, bri = asof_join_backward_uint32_t(left_values, right_values,
                                               allow_exact_matches, tolerance)
    fli, fri = asof_join_forward_uint32_t(left_values, right_values,
                                              allow_exact_matches, tolerance)

    for i in range(len(bri)):
        # choose timestamp from right with smaller difference
        if bri[i] != -1 and fri[i] != -1:
            bdiff = left_values[bli[i]] - right_values[bri[i]]
            fdiff = right_values[fri[i]] - left_values[fli[i]]
            right_indexer[i] = bri[i] if bdiff <= fdiff else fri[i]
        else:
            right_indexer[i] = bri[i] if bri[i] != -1 else fri[i]
        left_indexer[i] = bli[i]

    return left_indexer, right_indexer


def asof_join_backward_uint64_t(
        ndarray[uint64_t] left_values,
        ndarray[uint64_t] right_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        uint64_t tolerance_ = 0
        uint64_t diff = 0

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    right_pos = 0
    for left_pos in range(left_size):
        # restart right_pos if it went negative in a previous iteration
        if right_pos < 0:
            right_pos = 0

        # find last position in right whose value is less than left's
        if allow_exact_matches:
            while right_pos < right_size and\
                right_values[right_pos] <= left_values[left_pos]:
                right_pos += 1
        else:
            while right_pos < right_size and\
                right_values[right_pos] < left_values[left_pos]:
                right_pos += 1
        right_pos -= 1

        # save positions as the desired index
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and right_pos != -1:
            diff = left_values[left_pos] - right_values[right_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_forward_uint64_t(
        ndarray[uint64_t] left_values,
        ndarray[uint64_t] right_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        uint64_t tolerance_ = 0
        uint64_t diff = 0

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    right_pos = right_size - 1
    for left_pos in range(left_size - 1, -1, -1):
        # restart right_pos if it went over in a previous iteration
        if right_pos == right_size:
            right_pos = right_size - 1

        # find first position in right whose value is greater than left's
        if allow_exact_matches:
            while right_pos >= 0 and\
                right_values[right_pos] >= left_values[left_pos]:
                right_pos -= 1
        else:
            while right_pos >= 0 and\
                right_values[right_pos] > left_values[left_pos]:
                right_pos -= 1
        right_pos += 1

        # save positions as the desired index
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = right_pos\
                                  if right_pos != right_size else -1

        # if needed, verify that tolerance is met
        if has_tolerance and right_pos != right_size:
            diff = right_values[right_pos] - left_values[left_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_nearest_uint64_t(
        ndarray[uint64_t] left_values,
        ndarray[uint64_t] right_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_size, right_size, i
        ndarray[int64_t] left_indexer, right_indexer, bli, bri, fli, fri
        uint64_t bdiff, fdiff

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    # search both forward and backward
    bli, bri = asof_join_backward_uint64_t(left_values, right_values,
                                               allow_exact_matches, tolerance)
    fli, fri = asof_join_forward_uint64_t(left_values, right_values,
                                              allow_exact_matches, tolerance)

    for i in range(len(bri)):
        # choose timestamp from right with smaller difference
        if bri[i] != -1 and fri[i] != -1:
            bdiff = left_values[bli[i]] - right_values[bri[i]]
            fdiff = right_values[fri[i]] - left_values[fli[i]]
            right_indexer[i] = bri[i] if bdiff <= fdiff else fri[i]
        else:
            right_indexer[i] = bri[i] if bri[i] != -1 else fri[i]
        left_indexer[i] = bli[i]

    return left_indexer, right_indexer


def asof_join_backward_int8_t(
        ndarray[int8_t] left_values,
        ndarray[int8_t] right_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        int8_t tolerance_ = 0
        int8_t diff = 0

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    right_pos = 0
    for left_pos in range(left_size):
        # restart right_pos if it went negative in a previous iteration
        if right_pos < 0:
            right_pos = 0

        # find last position in right whose value is less than left's
        if allow_exact_matches:
            while right_pos < right_size and\
                right_values[right_pos] <= left_values[left_pos]:
                right_pos += 1
        else:
            while right_pos < right_size and\
                right_values[right_pos] < left_values[left_pos]:
                right_pos += 1
        right_pos -= 1

        # save positions as the desired index
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and right_pos != -1:
            diff = left_values[left_pos] - right_values[right_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_forward_int8_t(
        ndarray[int8_t] left_values,
        ndarray[int8_t] right_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        int8_t tolerance_ = 0
        int8_t diff = 0

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    right_pos = right_size - 1
    for left_pos in range(left_size - 1, -1, -1):
        # restart right_pos if it went over in a previous iteration
        if right_pos == right_size:
            right_pos = right_size - 1

        # find first position in right whose value is greater than left's
        if allow_exact_matches:
            while right_pos >= 0 and\
                right_values[right_pos] >= left_values[left_pos]:
                right_pos -= 1
        else:
            while right_pos >= 0 and\
                right_values[right_pos] > left_values[left_pos]:
                right_pos -= 1
        right_pos += 1

        # save positions as the desired index
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = right_pos\
                                  if right_pos != right_size else -1

        # if needed, verify that tolerance is met
        if has_tolerance and right_pos != right_size:
            diff = right_values[right_pos] - left_values[left_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_nearest_int8_t(
        ndarray[int8_t] left_values,
        ndarray[int8_t] right_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_size, right_size, i
        ndarray[int64_t] left_indexer, right_indexer, bli, bri, fli, fri
        int8_t bdiff, fdiff

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    # search both forward and backward
    bli, bri = asof_join_backward_int8_t(left_values, right_values,
                                               allow_exact_matches, tolerance)
    fli, fri = asof_join_forward_int8_t(left_values, right_values,
                                              allow_exact_matches, tolerance)

    for i in range(len(bri)):
        # choose timestamp from right with smaller difference
        if bri[i] != -1 and fri[i] != -1:
            bdiff = left_values[bli[i]] - right_values[bri[i]]
            fdiff = right_values[fri[i]] - left_values[fli[i]]
            right_indexer[i] = bri[i] if bdiff <= fdiff else fri[i]
        else:
            right_indexer[i] = bri[i] if bri[i] != -1 else fri[i]
        left_indexer[i] = bli[i]

    return left_indexer, right_indexer


def asof_join_backward_int16_t(
        ndarray[int16_t] left_values,
        ndarray[int16_t] right_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        int16_t tolerance_ = 0
        int16_t diff = 0

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    right_pos = 0
    for left_pos in range(left_size):
        # restart right_pos if it went negative in a previous iteration
        if right_pos < 0:
            right_pos = 0

        # find last position in right whose value is less than left's
        if allow_exact_matches:
            while right_pos < right_size and\
                right_values[right_pos] <= left_values[left_pos]:
                right_pos += 1
        else:
            while right_pos < right_size and\
                right_values[right_pos] < left_values[left_pos]:
                right_pos += 1
        right_pos -= 1

        # save positions as the desired index
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and right_pos != -1:
            diff = left_values[left_pos] - right_values[right_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_forward_int16_t(
        ndarray[int16_t] left_values,
        ndarray[int16_t] right_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        int16_t tolerance_ = 0
        int16_t diff = 0

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    right_pos = right_size - 1
    for left_pos in range(left_size - 1, -1, -1):
        # restart right_pos if it went over in a previous iteration
        if right_pos == right_size:
            right_pos = right_size - 1

        # find first position in right whose value is greater than left's
        if allow_exact_matches:
            while right_pos >= 0 and\
                right_values[right_pos] >= left_values[left_pos]:
                right_pos -= 1
        else:
            while right_pos >= 0 and\
                right_values[right_pos] > left_values[left_pos]:
                right_pos -= 1
        right_pos += 1

        # save positions as the desired index
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = right_pos\
                                  if right_pos != right_size else -1

        # if needed, verify that tolerance is met
        if has_tolerance and right_pos != right_size:
            diff = right_values[right_pos] - left_values[left_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_nearest_int16_t(
        ndarray[int16_t] left_values,
        ndarray[int16_t] right_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_size, right_size, i
        ndarray[int64_t] left_indexer, right_indexer, bli, bri, fli, fri
        int16_t bdiff, fdiff

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    # search both forward and backward
    bli, bri = asof_join_backward_int16_t(left_values, right_values,
                                               allow_exact_matches, tolerance)
    fli, fri = asof_join_forward_int16_t(left_values, right_values,
                                              allow_exact_matches, tolerance)

    for i in range(len(bri)):
        # choose timestamp from right with smaller difference
        if bri[i] != -1 and fri[i] != -1:
            bdiff = left_values[bli[i]] - right_values[bri[i]]
            fdiff = right_values[fri[i]] - left_values[fli[i]]
            right_indexer[i] = bri[i] if bdiff <= fdiff else fri[i]
        else:
            right_indexer[i] = bri[i] if bri[i] != -1 else fri[i]
        left_indexer[i] = bli[i]

    return left_indexer, right_indexer


def asof_join_backward_int32_t(
        ndarray[int32_t] left_values,
        ndarray[int32_t] right_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        int32_t tolerance_ = 0
        int32_t diff = 0

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    right_pos = 0
    for left_pos in range(left_size):
        # restart right_pos if it went negative in a previous iteration
        if right_pos < 0:
            right_pos = 0

        # find last position in right whose value is less than left's
        if allow_exact_matches:
            while right_pos < right_size and\
                right_values[right_pos] <= left_values[left_pos]:
                right_pos += 1
        else:
            while right_pos < right_size and\
                right_values[right_pos] < left_values[left_pos]:
                right_pos += 1
        right_pos -= 1

        # save positions as the desired index
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and right_pos != -1:
            diff = left_values[left_pos] - right_values[right_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_forward_int32_t(
        ndarray[int32_t] left_values,
        ndarray[int32_t] right_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        int32_t tolerance_ = 0
        int32_t diff = 0

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    right_pos = right_size - 1
    for left_pos in range(left_size - 1, -1, -1):
        # restart right_pos if it went over in a previous iteration
        if right_pos == right_size:
            right_pos = right_size - 1

        # find first position in right whose value is greater than left's
        if allow_exact_matches:
            while right_pos >= 0 and\
                right_values[right_pos] >= left_values[left_pos]:
                right_pos -= 1
        else:
            while right_pos >= 0 and\
                right_values[right_pos] > left_values[left_pos]:
                right_pos -= 1
        right_pos += 1

        # save positions as the desired index
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = right_pos\
                                  if right_pos != right_size else -1

        # if needed, verify that tolerance is met
        if has_tolerance and right_pos != right_size:
            diff = right_values[right_pos] - left_values[left_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_nearest_int32_t(
        ndarray[int32_t] left_values,
        ndarray[int32_t] right_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_size, right_size, i
        ndarray[int64_t] left_indexer, right_indexer, bli, bri, fli, fri
        int32_t bdiff, fdiff

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    # search both forward and backward
    bli, bri = asof_join_backward_int32_t(left_values, right_values,
                                               allow_exact_matches, tolerance)
    fli, fri = asof_join_forward_int32_t(left_values, right_values,
                                              allow_exact_matches, tolerance)

    for i in range(len(bri)):
        # choose timestamp from right with smaller difference
        if bri[i] != -1 and fri[i] != -1:
            bdiff = left_values[bli[i]] - right_values[bri[i]]
            fdiff = right_values[fri[i]] - left_values[fli[i]]
            right_indexer[i] = bri[i] if bdiff <= fdiff else fri[i]
        else:
            right_indexer[i] = bri[i] if bri[i] != -1 else fri[i]
        left_indexer[i] = bli[i]

    return left_indexer, right_indexer


def asof_join_backward_int64_t(
        ndarray[int64_t] left_values,
        ndarray[int64_t] right_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        int64_t tolerance_ = 0
        int64_t diff = 0

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    right_pos = 0
    for left_pos in range(left_size):
        # restart right_pos if it went negative in a previous iteration
        if right_pos < 0:
            right_pos = 0

        # find last position in right whose value is less than left's
        if allow_exact_matches:
            while right_pos < right_size and\
                right_values[right_pos] <= left_values[left_pos]:
                right_pos += 1
        else:
            while right_pos < right_size and\
                right_values[right_pos] < left_values[left_pos]:
                right_pos += 1
        right_pos -= 1

        # save positions as the desired index
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and right_pos != -1:
            diff = left_values[left_pos] - right_values[right_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_forward_int64_t(
        ndarray[int64_t] left_values,
        ndarray[int64_t] right_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        int64_t tolerance_ = 0
        int64_t diff = 0

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    right_pos = right_size - 1
    for left_pos in range(left_size - 1, -1, -1):
        # restart right_pos if it went over in a previous iteration
        if right_pos == right_size:
            right_pos = right_size - 1

        # find first position in right whose value is greater than left's
        if allow_exact_matches:
            while right_pos >= 0 and\
                right_values[right_pos] >= left_values[left_pos]:
                right_pos -= 1
        else:
            while right_pos >= 0 and\
                right_values[right_pos] > left_values[left_pos]:
                right_pos -= 1
        right_pos += 1

        # save positions as the desired index
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = right_pos\
                                  if right_pos != right_size else -1

        # if needed, verify that tolerance is met
        if has_tolerance and right_pos != right_size:
            diff = right_values[right_pos] - left_values[left_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_nearest_int64_t(
        ndarray[int64_t] left_values,
        ndarray[int64_t] right_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_size, right_size, i
        ndarray[int64_t] left_indexer, right_indexer, bli, bri, fli, fri
        int64_t bdiff, fdiff

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    # search both forward and backward
    bli, bri = asof_join_backward_int64_t(left_values, right_values,
                                               allow_exact_matches, tolerance)
    fli, fri = asof_join_forward_int64_t(left_values, right_values,
                                              allow_exact_matches, tolerance)

    for i in range(len(bri)):
        # choose timestamp from right with smaller difference
        if bri[i] != -1 and fri[i] != -1:
            bdiff = left_values[bli[i]] - right_values[bri[i]]
            fdiff = right_values[fri[i]] - left_values[fli[i]]
            right_indexer[i] = bri[i] if bdiff <= fdiff else fri[i]
        else:
            right_indexer[i] = bri[i] if bri[i] != -1 else fri[i]
        left_indexer[i] = bli[i]

    return left_indexer, right_indexer


def asof_join_backward_float(
        ndarray[float] left_values,
        ndarray[float] right_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        float tolerance_ = 0
        float diff = 0

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    right_pos = 0
    for left_pos in range(left_size):
        # restart right_pos if it went negative in a previous iteration
        if right_pos < 0:
            right_pos = 0

        # find last position in right whose value is less than left's
        if allow_exact_matches:
            while right_pos < right_size and\
                right_values[right_pos] <= left_values[left_pos]:
                right_pos += 1
        else:
            while right_pos < right_size and\
                right_values[right_pos] < left_values[left_pos]:
                right_pos += 1
        right_pos -= 1

        # save positions as the desired index
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and right_pos != -1:
            diff = left_values[left_pos] - right_values[right_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_forward_float(
        ndarray[float] left_values,
        ndarray[float] right_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        float tolerance_ = 0
        float diff = 0

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    right_pos = right_size - 1
    for left_pos in range(left_size - 1, -1, -1):
        # restart right_pos if it went over in a previous iteration
        if right_pos == right_size:
            right_pos = right_size - 1

        # find first position in right whose value is greater than left's
        if allow_exact_matches:
            while right_pos >= 0 and\
                right_values[right_pos] >= left_values[left_pos]:
                right_pos -= 1
        else:
            while right_pos >= 0 and\
                right_values[right_pos] > left_values[left_pos]:
                right_pos -= 1
        right_pos += 1

        # save positions as the desired index
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = right_pos\
                                  if right_pos != right_size else -1

        # if needed, verify that tolerance is met
        if has_tolerance and right_pos != right_size:
            diff = right_values[right_pos] - left_values[left_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_nearest_float(
        ndarray[float] left_values,
        ndarray[float] right_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_size, right_size, i
        ndarray[int64_t] left_indexer, right_indexer, bli, bri, fli, fri
        float bdiff, fdiff

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    # search both forward and backward
    bli, bri = asof_join_backward_float(left_values, right_values,
                                               allow_exact_matches, tolerance)
    fli, fri = asof_join_forward_float(left_values, right_values,
                                              allow_exact_matches, tolerance)

    for i in range(len(bri)):
        # choose timestamp from right with smaller difference
        if bri[i] != -1 and fri[i] != -1:
            bdiff = left_values[bli[i]] - right_values[bri[i]]
            fdiff = right_values[fri[i]] - left_values[fli[i]]
            right_indexer[i] = bri[i] if bdiff <= fdiff else fri[i]
        else:
            right_indexer[i] = bri[i] if bri[i] != -1 else fri[i]
        left_indexer[i] = bli[i]

    return left_indexer, right_indexer


def asof_join_backward_double(
        ndarray[double] left_values,
        ndarray[double] right_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        double tolerance_ = 0
        double diff = 0

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    right_pos = 0
    for left_pos in range(left_size):
        # restart right_pos if it went negative in a previous iteration
        if right_pos < 0:
            right_pos = 0

        # find last position in right whose value is less than left's
        if allow_exact_matches:
            while right_pos < right_size and\
                right_values[right_pos] <= left_values[left_pos]:
                right_pos += 1
        else:
            while right_pos < right_size and\
                right_values[right_pos] < left_values[left_pos]:
                right_pos += 1
        right_pos -= 1

        # save positions as the desired index
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = right_pos

        # if needed, verify that tolerance is met
        if has_tolerance and right_pos != -1:
            diff = left_values[left_pos] - right_values[right_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_forward_double(
        ndarray[double] left_values,
        ndarray[double] right_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_pos, right_pos, left_size, right_size
        ndarray[int64_t] left_indexer, right_indexer
        bint has_tolerance = 0
        double tolerance_ = 0
        double diff = 0

    # if we are using tolerance, set our objects
    if tolerance is not None:
        has_tolerance = 1
        tolerance_ = tolerance

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    right_pos = right_size - 1
    for left_pos in range(left_size - 1, -1, -1):
        # restart right_pos if it went over in a previous iteration
        if right_pos == right_size:
            right_pos = right_size - 1

        # find first position in right whose value is greater than left's
        if allow_exact_matches:
            while right_pos >= 0 and\
                right_values[right_pos] >= left_values[left_pos]:
                right_pos -= 1
        else:
            while right_pos >= 0 and\
                right_values[right_pos] > left_values[left_pos]:
                right_pos -= 1
        right_pos += 1

        # save positions as the desired index
        left_indexer[left_pos] = left_pos
        right_indexer[left_pos] = right_pos\
                                  if right_pos != right_size else -1

        # if needed, verify that tolerance is met
        if has_tolerance and right_pos != right_size:
            diff = right_values[right_pos] - left_values[left_pos]
            if diff > tolerance_:
                right_indexer[left_pos] = -1

    return left_indexer, right_indexer


def asof_join_nearest_double(
        ndarray[double] left_values,
        ndarray[double] right_values,
        bint allow_exact_matches=1,
        tolerance=None):

    cdef:
        Py_ssize_t left_size, right_size, i
        ndarray[int64_t] left_indexer, right_indexer, bli, bri, fli, fri
        double bdiff, fdiff

    left_size = len(left_values)
    right_size = len(right_values)

    left_indexer = np.empty(left_size, dtype=np.int64)
    right_indexer = np.empty(left_size, dtype=np.int64)

    # search both forward and backward
    bli, bri = asof_join_backward_double(left_values, right_values,
                                               allow_exact_matches, tolerance)
    fli, fri = asof_join_forward_double(left_values, right_values,
                                              allow_exact_matches, tolerance)

    for i in range(len(bri)):
        # choose timestamp from right with smaller difference
        if bri[i] != -1 and fri[i] != -1:
            bdiff = left_values[bli[i]] - right_values[bri[i]]
            fdiff = right_values[fri[i]] - left_values[fli[i]]
            right_indexer[i] = bri[i] if bdiff <= fdiff else fri[i]
        else:
            right_indexer[i] = bri[i] if bri[i] != -1 else fri[i]
        left_indexer[i] = bli[i]

    return left_indexer, right_indexer
