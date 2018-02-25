# cython: profile=False

cimport cython

from cpython cimport (PyObject, Py_INCREF, PyList_Check, PyTuple_Check,
                      PyMem_Malloc, PyMem_Realloc, PyMem_Free,
                      PyString_Check, PyBytes_Check,
                      PyUnicode_Check)

from libc.stdlib cimport malloc, free

import numpy as np
cimport numpy as cnp
from numpy cimport ndarray, uint8_t, uint32_t
cnp.import_array()

cdef extern from "numpy/npy_math.h":
    double NAN "NPY_NAN"


from khash cimport (
    khiter_t,

    kh_str_t, kh_init_str, kh_put_str, kh_exist_str,
    kh_get_str, kh_destroy_str, kh_resize_str,

    kh_put_strbox, kh_get_strbox, kh_init_strbox,

    kh_int64_t, kh_init_int64, kh_resize_int64, kh_destroy_int64,
    kh_get_int64, kh_exist_int64, kh_put_int64,

    kh_float64_t, kh_exist_float64, kh_put_float64, kh_init_float64,
    kh_get_float64, kh_destroy_float64, kh_resize_float64,

    kh_resize_uint64, kh_exist_uint64, kh_destroy_uint64, kh_put_uint64,
    kh_get_uint64, kh_init_uint64,

    kh_destroy_pymap, kh_exist_pymap, kh_init_pymap, kh_get_pymap,
    kh_put_pymap, kh_resize_pymap)


from util cimport _checknan
cimport util

from missing cimport checknull


nan = np.nan

cdef int64_t iNaT = util.get_nat()
_SIZE_HINT_LIMIT = (1 << 20) + 7


cdef size_t _INIT_VEC_CAP = 128

include "hashtable_class_helper.pxi"
include "hashtable_func_helper.pxi"

cdef class Factorizer:
    cdef public PyObjectHashTable table
    cdef public ObjectVector uniques
    cdef public Py_ssize_t count

    def __init__(self, size_hint):
        self.table = PyObjectHashTable(size_hint)
        self.uniques = ObjectVector()
        self.count = 0

    def get_count(self):
        return self.count

    def factorize(self, ndarray[object] values, sort=False, na_sentinel=-1,
                  check_null=True):
        """
        Factorize values with nans replaced by na_sentinel
        >>> factorize(np.array([1,2,np.nan], dtype='O'), na_sentinel=20)
        array([ 0,  1, 20])
        """
        if self.uniques.external_view_exists:
            uniques = ObjectVector()
            uniques.extend(self.uniques.to_array())
            self.uniques = uniques
        labels = self.table.get_labels(values, self.uniques,
                                       self.count, na_sentinel, check_null)
        mask = (labels == na_sentinel)
        # sort on
        if sort:
            if labels.dtype != np.intp:
                labels = labels.astype(np.intp)
            sorter = self.uniques.to_array().argsort()
            reverse_indexer = np.empty(len(sorter), dtype=np.intp)
            reverse_indexer.put(sorter, np.arange(len(sorter)))
            labels = reverse_indexer.take(labels, mode='clip')
            labels[mask] = na_sentinel
        self.count = len(self.uniques)
        return labels

    def unique(self, ndarray[object] values):
        # just for fun
        return self.table.unique(values)


cdef class Int64Factorizer:
    cdef public Int64HashTable table
    cdef public Int64Vector uniques
    cdef public Py_ssize_t count

    def __init__(self, size_hint):
        self.table = Int64HashTable(size_hint)
        self.uniques = Int64Vector()
        self.count = 0

    def get_count(self):
        return self.count

    def factorize(self, int64_t[:] values, sort=False,
                  na_sentinel=-1, check_null=True):
        """
        Factorize values with nans replaced by na_sentinel
        >>> factorize(np.array([1,2,np.nan], dtype='O'), na_sentinel=20)
        array([ 0,  1, 20])
        """
        if self.uniques.external_view_exists:
            uniques = Int64Vector()
            uniques.extend(self.uniques.to_array())
            self.uniques = uniques
        labels = self.table.get_labels(values, self.uniques,
                                       self.count, na_sentinel,
                                       check_null)

        # sort on
        if sort:
            if labels.dtype != np.intp:
                labels = labels.astype(np.intp)

            sorter = self.uniques.to_array().argsort()
            reverse_indexer = np.empty(len(sorter), dtype=np.intp)
            reverse_indexer.put(sorter, np.arange(len(sorter)))

            labels = reverse_indexer.take(labels)

        self.count = len(self.uniques)
        return labels


@cython.wraparound(False)
@cython.boundscheck(False)
def unique_label_indices(ndarray[int64_t, ndim=1] labels):
    """
    indices of the first occurrences of the unique labels
    *excluding* -1. equivalent to:
        np.unique(labels, return_index=True)[1]
    """
    cdef:
        int ret = 0
        Py_ssize_t i, n = len(labels)
        kh_int64_t * table = kh_init_int64()
        Int64Vector idx = Int64Vector()
        ndarray[int64_t, ndim=1] arr
        Int64VectorData *ud = idx.data

    kh_resize_int64(table, min(n, _SIZE_HINT_LIMIT))

    with nogil:
        for i in range(n):
            kh_put_int64(table, labels[i], &ret)
            if ret != 0:
                if needs_resize(ud):
                    with gil:
                        idx.resize()
                append_data_int64(ud, i)

    kh_destroy_int64(table)

    arr = idx.to_array()
    arr = arr[labels[arr].argsort()]

    return arr[1:] if arr.size != 0 and labels[arr[0]] == -1 else arr
