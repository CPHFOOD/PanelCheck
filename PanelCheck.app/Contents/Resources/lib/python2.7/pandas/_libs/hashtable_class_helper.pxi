"""
Template for each `dtype` helper function for hashtable

WARNING: DO NOT edit .pxi FILE directly, .pxi is generated from .pxi.in
"""

from missing cimport is_null_datetimelike


#----------------------------------------------------------------------
# VectorData
#----------------------------------------------------------------------

ctypedef struct Float64VectorData:
    float64_t *data
    size_t n, m


@cython.wraparound(False)
@cython.boundscheck(False)
cdef inline void append_data_float64(Float64VectorData *data,
                                       float64_t x) nogil:

    data.data[data.n] = x
    data.n += 1


@cython.wraparound(False)
@cython.boundscheck(False)
cdef inline void append_data_int64(Int64VectorData *data,
                                       int64_t x) nogil:

    data.data[data.n] = x
    data.n += 1

ctypedef struct StringVectorData:
    char * *data
    size_t n, m


@cython.wraparound(False)
@cython.boundscheck(False)
cdef inline void append_data_string(StringVectorData *data,
                                       char * x) nogil:

    data.data[data.n] = x
    data.n += 1

ctypedef struct UInt64VectorData:
    uint64_t *data
    size_t n, m


@cython.wraparound(False)
@cython.boundscheck(False)
cdef inline void append_data_uint64(UInt64VectorData *data,
                                       uint64_t x) nogil:

    data.data[data.n] = x
    data.n += 1

ctypedef fused vector_data:
    Int64VectorData
    UInt64VectorData
    Float64VectorData
    StringVectorData

cdef inline bint needs_resize(vector_data *data) nogil:
    return data.n == data.m

#----------------------------------------------------------------------
# Vector
#----------------------------------------------------------------------

cdef class Float64Vector:

    cdef:
        bint external_view_exists
        Float64VectorData *data
        ndarray ao

    def __cinit__(self):
        self.data = <Float64VectorData *>PyMem_Malloc(
            sizeof(Float64VectorData))
        if not self.data:
            raise MemoryError()
        self.external_view_exists = False
        self.data.n = 0
        self.data.m = _INIT_VEC_CAP
        self.ao = np.empty(self.data.m, dtype=np.float64)
        self.data.data = <float64_t*> self.ao.data

    cdef resize(self):
        self.data.m = max(self.data.m * 4, _INIT_VEC_CAP)
        self.ao.resize(self.data.m, refcheck=False)
        self.data.data = <float64_t*> self.ao.data

    def __dealloc__(self):
        if self.data is not NULL:
            PyMem_Free(self.data)
            self.data = NULL

    def __len__(self):
        return self.data.n

    cpdef to_array(self):
        if self.data.m != self.data.n:
            if self.external_view_exists:
                # should never happen
                raise ValueError("should have raised on append()")
            self.ao.resize(self.data.n, refcheck=False)
            self.data.m = self.data.n
        self.external_view_exists = True
        return self.ao

    cdef inline void append(self, float64_t x):

        if needs_resize(self.data):
            if self.external_view_exists:
                raise ValueError("external reference but Vector.resize() needed")
            self.resize()

        append_data_float64(self.data, x)

    cdef extend(self, float64_t[:] x):
        for i in range(len(x)):
            self.append(x[i])

cdef class UInt64Vector:

    cdef:
        bint external_view_exists
        UInt64VectorData *data
        ndarray ao

    def __cinit__(self):
        self.data = <UInt64VectorData *>PyMem_Malloc(
            sizeof(UInt64VectorData))
        if not self.data:
            raise MemoryError()
        self.external_view_exists = False
        self.data.n = 0
        self.data.m = _INIT_VEC_CAP
        self.ao = np.empty(self.data.m, dtype=np.uint64)
        self.data.data = <uint64_t*> self.ao.data

    cdef resize(self):
        self.data.m = max(self.data.m * 4, _INIT_VEC_CAP)
        self.ao.resize(self.data.m, refcheck=False)
        self.data.data = <uint64_t*> self.ao.data

    def __dealloc__(self):
        if self.data is not NULL:
            PyMem_Free(self.data)
            self.data = NULL

    def __len__(self):
        return self.data.n

    cpdef to_array(self):
        if self.data.m != self.data.n:
            if self.external_view_exists:
                # should never happen
                raise ValueError("should have raised on append()")
            self.ao.resize(self.data.n, refcheck=False)
            self.data.m = self.data.n
        self.external_view_exists = True
        return self.ao

    cdef inline void append(self, uint64_t x):

        if needs_resize(self.data):
            if self.external_view_exists:
                raise ValueError("external reference but Vector.resize() needed")
            self.resize()

        append_data_uint64(self.data, x)

    cdef extend(self, uint64_t[:] x):
        for i in range(len(x)):
            self.append(x[i])

cdef class Int64Vector:


    def __cinit__(self):
        self.data = <Int64VectorData *>PyMem_Malloc(
            sizeof(Int64VectorData))
        if not self.data:
            raise MemoryError()
        self.external_view_exists = False
        self.data.n = 0
        self.data.m = _INIT_VEC_CAP
        self.ao = np.empty(self.data.m, dtype=np.int64)
        self.data.data = <int64_t*> self.ao.data

    cdef resize(self):
        self.data.m = max(self.data.m * 4, _INIT_VEC_CAP)
        self.ao.resize(self.data.m, refcheck=False)
        self.data.data = <int64_t*> self.ao.data

    def __dealloc__(self):
        if self.data is not NULL:
            PyMem_Free(self.data)
            self.data = NULL

    def __len__(self):
        return self.data.n

    cpdef to_array(self):
        if self.data.m != self.data.n:
            if self.external_view_exists:
                # should never happen
                raise ValueError("should have raised on append()")
            self.ao.resize(self.data.n, refcheck=False)
            self.data.m = self.data.n
        self.external_view_exists = True
        return self.ao

    cdef inline void append(self, int64_t x):

        if needs_resize(self.data):
            if self.external_view_exists:
                raise ValueError("external reference but Vector.resize() needed")
            self.resize()

        append_data_int64(self.data, x)

    cdef extend(self, int64_t[:] x):
        for i in range(len(x)):
            self.append(x[i])

cdef class StringVector:

    cdef:
        StringVectorData *data
        bint external_view_exists

    def __cinit__(self):
        self.data = <StringVectorData *>PyMem_Malloc(
            sizeof(StringVectorData))
        if not self.data:
            raise MemoryError()
        self.external_view_exists = False
        self.data.n = 0
        self.data.m = _INIT_VEC_CAP
        self.data.data = <char **> malloc(self.data.m * sizeof(char *))
        if not self.data.data:
            raise MemoryError()

    cdef resize(self):
        cdef:
            char **orig_data
            size_t i, m

        m = self.data.m
        self.data.m = max(self.data.m * 4, _INIT_VEC_CAP)

        orig_data = self.data.data
        self.data.data = <char **> malloc(self.data.m * sizeof(char *))
        if not self.data.data:
            raise MemoryError()
        for i in range(m):
            self.data.data[i] = orig_data[i]

    def __dealloc__(self):
        if self.data is not NULL:
            if self.data.data is not NULL:
                free(self.data.data)
            PyMem_Free(self.data)
            self.data = NULL

    def __len__(self):
        return self.data.n

    def to_array(self):
        cdef:
            ndarray ao
            size_t n
            object val

        ao = np.empty(self.data.n, dtype=np.object)
        for i in range(self.data.n):
            val = self.data.data[i]
            ao[i] = val
        self.external_view_exists = True
        self.data.m = self.data.n
        return ao

    cdef inline void append(self, char * x):

        if needs_resize(self.data):
            self.resize()

        append_data_string(self.data, x)

    cdef extend(self, ndarray[:] x):
        for i in range(len(x)):
            self.append(x[i])

cdef class ObjectVector:

    cdef:
        PyObject **data
        size_t n, m
        ndarray ao
        bint external_view_exists

    def __cinit__(self):
        self.external_view_exists = False
        self.n = 0
        self.m = _INIT_VEC_CAP
        self.ao = np.empty(_INIT_VEC_CAP, dtype=object)
        self.data = <PyObject**> self.ao.data

    def __len__(self):
        return self.n

    cdef inline append(self, object o):
        if self.n == self.m:
            if self.external_view_exists:
                raise ValueError("external reference but Vector.resize() needed")
            self.m = max(self.m * 2, _INIT_VEC_CAP)
            self.ao.resize(self.m, refcheck=False)
            self.data = <PyObject**> self.ao.data

        Py_INCREF(o)
        self.data[self.n] = <PyObject*> o
        self.n += 1

    def to_array(self):
        if self.m != self.n:
            if self.external_view_exists:
                raise ValueError("should have raised on append()")
            self.ao.resize(self.n, refcheck=False)
            self.m = self.n
        self.external_view_exists = True
        return self.ao

    cdef extend(self, ndarray[:] x):
        for i in range(len(x)):
            self.append(x[i])

#----------------------------------------------------------------------
# HashTable
#----------------------------------------------------------------------


cdef class HashTable:

    pass

cdef class Float64HashTable(HashTable):

    def __cinit__(self, size_hint=1):
        self.table = kh_init_float64()
        if size_hint is not None:
            kh_resize_float64(self.table, size_hint)

    def __len__(self):
        return self.table.size

    def __dealloc__(self):
        if self.table is not NULL:
            kh_destroy_float64(self.table)
            self.table = NULL

    def __contains__(self, object key):
        cdef khiter_t k
        k = kh_get_float64(self.table, key)
        return k != self.table.n_buckets

    def sizeof(self, deep=False):
        """ return the size of my table in bytes """
        return self.table.n_buckets * (sizeof(float64_t) + # keys
                                       sizeof(size_t) + # vals
                                       sizeof(uint32_t)) # flags

    cpdef get_item(self, float64_t val):
        cdef khiter_t k
        k = kh_get_float64(self.table, val)
        if k != self.table.n_buckets:
            return self.table.vals[k]
        else:
            raise KeyError(val)

    cpdef set_item(self, float64_t key, Py_ssize_t val):
        cdef:
            khiter_t k
            int ret = 0

        k = kh_put_float64(self.table, key, &ret)
        self.table.keys[k] = key
        if kh_exist_float64(self.table, k):
            self.table.vals[k] = val
        else:
            raise KeyError(key)

    @cython.boundscheck(False)
    def map(self, float64_t[:] keys, int64_t[:] values):
        cdef:
            Py_ssize_t i, n = len(values)
            int ret = 0
            float64_t key
            khiter_t k

        with nogil:
            for i in range(n):
                key = keys[i]
                k = kh_put_float64(self.table, key, &ret)
                self.table.vals[k] = <Py_ssize_t> values[i]

    @cython.boundscheck(False)
    def map_locations(self, ndarray[float64_t, ndim=1] values):
        cdef:
            Py_ssize_t i, n = len(values)
            int ret = 0
            float64_t val
            khiter_t k

        with nogil:
            for i in range(n):
                val = values[i]
                k = kh_put_float64(self.table, val, &ret)
                self.table.vals[k] = i

    @cython.boundscheck(False)
    def lookup(self, float64_t[:] values):
        cdef:
            Py_ssize_t i, n = len(values)
            int ret = 0
            float64_t val
            khiter_t k
            int64_t[:] locs = np.empty(n, dtype=np.int64)

        with nogil:
            for i in range(n):
                val = values[i]
                k = kh_get_float64(self.table, val)
                if k != self.table.n_buckets:
                    locs[i] = self.table.vals[k]
                else:
                    locs[i] = -1

        return np.asarray(locs)

    def factorize(self, float64_t values):
        uniques = Float64Vector()
        labels = self.get_labels(values, uniques, 0, 0)
        return uniques.to_array(), labels

    @cython.boundscheck(False)
    def get_labels(self, float64_t[:] values, Float64Vector uniques,
                   Py_ssize_t count_prior, Py_ssize_t na_sentinel,
                   bint check_null=True):
        cdef:
            Py_ssize_t i, n = len(values)
            int64_t[:] labels
            Py_ssize_t idx, count = count_prior
            int ret = 0
            float64_t val
            khiter_t k
            Float64VectorData *ud

        labels = np.empty(n, dtype=np.int64)
        ud = uniques.data

        with nogil:
            for i in range(n):
                val = values[i]

                if check_null and val != val:
                    labels[i] = na_sentinel
                    continue

                k = kh_get_float64(self.table, val)

                if k != self.table.n_buckets:
                    idx = self.table.vals[k]
                    labels[i] = idx
                else:
                    k = kh_put_float64(self.table, val, &ret)
                    self.table.vals[k] = count

                    if needs_resize(ud):
                        with gil:
                            if uniques.external_view_exists:
                                raise ValueError("external reference to uniques held, "
                                        "but Vector.resize() needed")
                            uniques.resize()
                    append_data_float64(ud, val)
                    labels[i] = count
                    count += 1

        return np.asarray(labels)

    @cython.boundscheck(False)
    def get_labels_groupby(self, float64_t[:] values):
        cdef:
            Py_ssize_t i, n = len(values)
            int64_t[:] labels
            Py_ssize_t idx, count = 0
            int ret = 0
            float64_t val
            khiter_t k
            Float64Vector uniques = Float64Vector()
            Float64VectorData *ud

        labels = np.empty(n, dtype=np.int64)
        ud = uniques.data

        with nogil:
            for i in range(n):
                val = values[i]

                # specific for groupby
                if val < 0:
                    labels[i] = -1
                    continue

                k = kh_get_float64(self.table, val)
                if k != self.table.n_buckets:
                    idx = self.table.vals[k]
                    labels[i] = idx
                else:
                    k = kh_put_float64(self.table, val, &ret)
                    self.table.vals[k] = count

                    if needs_resize(ud):
                        with gil:
                            uniques.resize()
                    append_data_float64(ud, val)
                    labels[i] = count
                    count += 1

        arr_uniques = uniques.to_array()

        return np.asarray(labels), arr_uniques

    @cython.boundscheck(False)
    def unique(self, ndarray[float64_t, ndim=1] values):
        if values.flags.writeable:
          # If the value is writeable (mutable) then use memview
          return self.unique_memview(values)

        # We cannot use the memoryview version on readonly-buffers due to
        # a limitation of Cython's typed memoryviews. Instead we can use
        # the slightly slower Cython ndarray type directly.
        # see https://github.com/cython/cython/issues/1605
        cdef:
           Py_ssize_t i, n = len(values)
           int ret = 0
           float64_t val
           khiter_t k
           bint seen_na = 0
           Float64Vector uniques = Float64Vector()
           Float64VectorData *ud

        ud = uniques.data

        with nogil:
            for i in range(n):
                val = values[i]
                IF True:
                  if val == val:
                      k = kh_get_float64(self.table, val)
                      if k == self.table.n_buckets:
                          kh_put_float64(self.table, val, &ret)
                          if needs_resize(ud):
                              with gil:
                                  uniques.resize()
                          append_data_float64(ud, val)
                  elif not seen_na:
                      seen_na = 1
                      if needs_resize(ud):
                          with gil:
                              uniques.resize()
                      append_data_float64(ud, NAN)
                ELSE:
                  k = kh_get_float64(self.table, val)
                  if k == self.table.n_buckets:
                      kh_put_float64(self.table, val, &ret)
                      if needs_resize(ud):
                          with gil:
                              uniques.resize()
                      append_data_float64(ud, val)
        return uniques.to_array()
      

    @cython.boundscheck(False)
    def unique_memview(self, float64_t[:] values):
        cdef:
           Py_ssize_t i, n = len(values)
           int ret = 0
           float64_t val
           khiter_t k
           bint seen_na = 0
           Float64Vector uniques = Float64Vector()
           Float64VectorData *ud

        ud = uniques.data

        with nogil:
            for i in range(n):
                val = values[i]
                IF True:
                  if val == val:
                      k = kh_get_float64(self.table, val)
                      if k == self.table.n_buckets:
                          kh_put_float64(self.table, val, &ret)
                          if needs_resize(ud):
                              with gil:
                                  uniques.resize()
                          append_data_float64(ud, val)
                  elif not seen_na:
                      seen_na = 1
                      if needs_resize(ud):
                          with gil:
                              uniques.resize()
                      append_data_float64(ud, NAN)
                ELSE:
                  k = kh_get_float64(self.table, val)
                  if k == self.table.n_buckets:
                      kh_put_float64(self.table, val, &ret)
                      if needs_resize(ud):
                          with gil:
                              uniques.resize()
                      append_data_float64(ud, val)
        return uniques.to_array()
      

cdef class UInt64HashTable(HashTable):

    def __cinit__(self, size_hint=1):
        self.table = kh_init_uint64()
        if size_hint is not None:
            kh_resize_uint64(self.table, size_hint)

    def __len__(self):
        return self.table.size

    def __dealloc__(self):
        if self.table is not NULL:
            kh_destroy_uint64(self.table)
            self.table = NULL

    def __contains__(self, object key):
        cdef khiter_t k
        k = kh_get_uint64(self.table, key)
        return k != self.table.n_buckets

    def sizeof(self, deep=False):
        """ return the size of my table in bytes """
        return self.table.n_buckets * (sizeof(uint64_t) + # keys
                                       sizeof(size_t) + # vals
                                       sizeof(uint32_t)) # flags

    cpdef get_item(self, uint64_t val):
        cdef khiter_t k
        k = kh_get_uint64(self.table, val)
        if k != self.table.n_buckets:
            return self.table.vals[k]
        else:
            raise KeyError(val)

    cpdef set_item(self, uint64_t key, Py_ssize_t val):
        cdef:
            khiter_t k
            int ret = 0

        k = kh_put_uint64(self.table, key, &ret)
        self.table.keys[k] = key
        if kh_exist_uint64(self.table, k):
            self.table.vals[k] = val
        else:
            raise KeyError(key)

    @cython.boundscheck(False)
    def map(self, uint64_t[:] keys, int64_t[:] values):
        cdef:
            Py_ssize_t i, n = len(values)
            int ret = 0
            uint64_t key
            khiter_t k

        with nogil:
            for i in range(n):
                key = keys[i]
                k = kh_put_uint64(self.table, key, &ret)
                self.table.vals[k] = <Py_ssize_t> values[i]

    @cython.boundscheck(False)
    def map_locations(self, ndarray[uint64_t, ndim=1] values):
        cdef:
            Py_ssize_t i, n = len(values)
            int ret = 0
            uint64_t val
            khiter_t k

        with nogil:
            for i in range(n):
                val = values[i]
                k = kh_put_uint64(self.table, val, &ret)
                self.table.vals[k] = i

    @cython.boundscheck(False)
    def lookup(self, uint64_t[:] values):
        cdef:
            Py_ssize_t i, n = len(values)
            int ret = 0
            uint64_t val
            khiter_t k
            int64_t[:] locs = np.empty(n, dtype=np.int64)

        with nogil:
            for i in range(n):
                val = values[i]
                k = kh_get_uint64(self.table, val)
                if k != self.table.n_buckets:
                    locs[i] = self.table.vals[k]
                else:
                    locs[i] = -1

        return np.asarray(locs)

    def factorize(self, uint64_t values):
        uniques = UInt64Vector()
        labels = self.get_labels(values, uniques, 0, 0)
        return uniques.to_array(), labels

    @cython.boundscheck(False)
    def get_labels(self, uint64_t[:] values, UInt64Vector uniques,
                   Py_ssize_t count_prior, Py_ssize_t na_sentinel,
                   bint check_null=True):
        cdef:
            Py_ssize_t i, n = len(values)
            int64_t[:] labels
            Py_ssize_t idx, count = count_prior
            int ret = 0
            uint64_t val
            khiter_t k
            UInt64VectorData *ud

        labels = np.empty(n, dtype=np.int64)
        ud = uniques.data

        with nogil:
            for i in range(n):
                val = values[i]

                if check_null and False:
                    labels[i] = na_sentinel
                    continue

                k = kh_get_uint64(self.table, val)

                if k != self.table.n_buckets:
                    idx = self.table.vals[k]
                    labels[i] = idx
                else:
                    k = kh_put_uint64(self.table, val, &ret)
                    self.table.vals[k] = count

                    if needs_resize(ud):
                        with gil:
                            if uniques.external_view_exists:
                                raise ValueError("external reference to uniques held, "
                                        "but Vector.resize() needed")
                            uniques.resize()
                    append_data_uint64(ud, val)
                    labels[i] = count
                    count += 1

        return np.asarray(labels)

    @cython.boundscheck(False)
    def get_labels_groupby(self, uint64_t[:] values):
        cdef:
            Py_ssize_t i, n = len(values)
            int64_t[:] labels
            Py_ssize_t idx, count = 0
            int ret = 0
            uint64_t val
            khiter_t k
            UInt64Vector uniques = UInt64Vector()
            UInt64VectorData *ud

        labels = np.empty(n, dtype=np.int64)
        ud = uniques.data

        with nogil:
            for i in range(n):
                val = values[i]

                # specific for groupby

                k = kh_get_uint64(self.table, val)
                if k != self.table.n_buckets:
                    idx = self.table.vals[k]
                    labels[i] = idx
                else:
                    k = kh_put_uint64(self.table, val, &ret)
                    self.table.vals[k] = count

                    if needs_resize(ud):
                        with gil:
                            uniques.resize()
                    append_data_uint64(ud, val)
                    labels[i] = count
                    count += 1

        arr_uniques = uniques.to_array()

        return np.asarray(labels), arr_uniques

    @cython.boundscheck(False)
    def unique(self, ndarray[uint64_t, ndim=1] values):
        if values.flags.writeable:
          # If the value is writeable (mutable) then use memview
          return self.unique_memview(values)

        # We cannot use the memoryview version on readonly-buffers due to
        # a limitation of Cython's typed memoryviews. Instead we can use
        # the slightly slower Cython ndarray type directly.
        # see https://github.com/cython/cython/issues/1605
        cdef:
           Py_ssize_t i, n = len(values)
           int ret = 0
           uint64_t val
           khiter_t k
           bint seen_na = 0
           UInt64Vector uniques = UInt64Vector()
           UInt64VectorData *ud

        ud = uniques.data

        with nogil:
            for i in range(n):
                val = values[i]
                IF False:
                  if val == val:
                      k = kh_get_uint64(self.table, val)
                      if k == self.table.n_buckets:
                          kh_put_uint64(self.table, val, &ret)
                          if needs_resize(ud):
                              with gil:
                                  uniques.resize()
                          append_data_uint64(ud, val)
                  elif not seen_na:
                      seen_na = 1
                      if needs_resize(ud):
                          with gil:
                              uniques.resize()
                      append_data_uint64(ud, NAN)
                ELSE:
                  k = kh_get_uint64(self.table, val)
                  if k == self.table.n_buckets:
                      kh_put_uint64(self.table, val, &ret)
                      if needs_resize(ud):
                          with gil:
                              uniques.resize()
                      append_data_uint64(ud, val)
        return uniques.to_array()
      

    @cython.boundscheck(False)
    def unique_memview(self, uint64_t[:] values):
        cdef:
           Py_ssize_t i, n = len(values)
           int ret = 0
           uint64_t val
           khiter_t k
           bint seen_na = 0
           UInt64Vector uniques = UInt64Vector()
           UInt64VectorData *ud

        ud = uniques.data

        with nogil:
            for i in range(n):
                val = values[i]
                IF False:
                  if val == val:
                      k = kh_get_uint64(self.table, val)
                      if k == self.table.n_buckets:
                          kh_put_uint64(self.table, val, &ret)
                          if needs_resize(ud):
                              with gil:
                                  uniques.resize()
                          append_data_uint64(ud, val)
                  elif not seen_na:
                      seen_na = 1
                      if needs_resize(ud):
                          with gil:
                              uniques.resize()
                      append_data_uint64(ud, NAN)
                ELSE:
                  k = kh_get_uint64(self.table, val)
                  if k == self.table.n_buckets:
                      kh_put_uint64(self.table, val, &ret)
                      if needs_resize(ud):
                          with gil:
                              uniques.resize()
                      append_data_uint64(ud, val)
        return uniques.to_array()
      

cdef class Int64HashTable(HashTable):

    def __cinit__(self, size_hint=1):
        self.table = kh_init_int64()
        if size_hint is not None:
            kh_resize_int64(self.table, size_hint)

    def __len__(self):
        return self.table.size

    def __dealloc__(self):
        if self.table is not NULL:
            kh_destroy_int64(self.table)
            self.table = NULL

    def __contains__(self, object key):
        cdef khiter_t k
        k = kh_get_int64(self.table, key)
        return k != self.table.n_buckets

    def sizeof(self, deep=False):
        """ return the size of my table in bytes """
        return self.table.n_buckets * (sizeof(int64_t) + # keys
                                       sizeof(size_t) + # vals
                                       sizeof(uint32_t)) # flags

    cpdef get_item(self, int64_t val):
        cdef khiter_t k
        k = kh_get_int64(self.table, val)
        if k != self.table.n_buckets:
            return self.table.vals[k]
        else:
            raise KeyError(val)

    cpdef set_item(self, int64_t key, Py_ssize_t val):
        cdef:
            khiter_t k
            int ret = 0

        k = kh_put_int64(self.table, key, &ret)
        self.table.keys[k] = key
        if kh_exist_int64(self.table, k):
            self.table.vals[k] = val
        else:
            raise KeyError(key)

    @cython.boundscheck(False)
    def map(self, int64_t[:] keys, int64_t[:] values):
        cdef:
            Py_ssize_t i, n = len(values)
            int ret = 0
            int64_t key
            khiter_t k

        with nogil:
            for i in range(n):
                key = keys[i]
                k = kh_put_int64(self.table, key, &ret)
                self.table.vals[k] = <Py_ssize_t> values[i]

    @cython.boundscheck(False)
    def map_locations(self, ndarray[int64_t, ndim=1] values):
        cdef:
            Py_ssize_t i, n = len(values)
            int ret = 0
            int64_t val
            khiter_t k

        with nogil:
            for i in range(n):
                val = values[i]
                k = kh_put_int64(self.table, val, &ret)
                self.table.vals[k] = i

    @cython.boundscheck(False)
    def lookup(self, int64_t[:] values):
        cdef:
            Py_ssize_t i, n = len(values)
            int ret = 0
            int64_t val
            khiter_t k
            int64_t[:] locs = np.empty(n, dtype=np.int64)

        with nogil:
            for i in range(n):
                val = values[i]
                k = kh_get_int64(self.table, val)
                if k != self.table.n_buckets:
                    locs[i] = self.table.vals[k]
                else:
                    locs[i] = -1

        return np.asarray(locs)

    def factorize(self, int64_t values):
        uniques = Int64Vector()
        labels = self.get_labels(values, uniques, 0, 0)
        return uniques.to_array(), labels

    @cython.boundscheck(False)
    def get_labels(self, int64_t[:] values, Int64Vector uniques,
                   Py_ssize_t count_prior, Py_ssize_t na_sentinel,
                   bint check_null=True):
        cdef:
            Py_ssize_t i, n = len(values)
            int64_t[:] labels
            Py_ssize_t idx, count = count_prior
            int ret = 0
            int64_t val
            khiter_t k
            Int64VectorData *ud

        labels = np.empty(n, dtype=np.int64)
        ud = uniques.data

        with nogil:
            for i in range(n):
                val = values[i]

                if check_null and val == iNaT:
                    labels[i] = na_sentinel
                    continue

                k = kh_get_int64(self.table, val)

                if k != self.table.n_buckets:
                    idx = self.table.vals[k]
                    labels[i] = idx
                else:
                    k = kh_put_int64(self.table, val, &ret)
                    self.table.vals[k] = count

                    if needs_resize(ud):
                        with gil:
                            if uniques.external_view_exists:
                                raise ValueError("external reference to uniques held, "
                                        "but Vector.resize() needed")
                            uniques.resize()
                    append_data_int64(ud, val)
                    labels[i] = count
                    count += 1

        return np.asarray(labels)

    @cython.boundscheck(False)
    def get_labels_groupby(self, int64_t[:] values):
        cdef:
            Py_ssize_t i, n = len(values)
            int64_t[:] labels
            Py_ssize_t idx, count = 0
            int ret = 0
            int64_t val
            khiter_t k
            Int64Vector uniques = Int64Vector()
            Int64VectorData *ud

        labels = np.empty(n, dtype=np.int64)
        ud = uniques.data

        with nogil:
            for i in range(n):
                val = values[i]

                # specific for groupby
                if val < 0:
                    labels[i] = -1
                    continue

                k = kh_get_int64(self.table, val)
                if k != self.table.n_buckets:
                    idx = self.table.vals[k]
                    labels[i] = idx
                else:
                    k = kh_put_int64(self.table, val, &ret)
                    self.table.vals[k] = count

                    if needs_resize(ud):
                        with gil:
                            uniques.resize()
                    append_data_int64(ud, val)
                    labels[i] = count
                    count += 1

        arr_uniques = uniques.to_array()

        return np.asarray(labels), arr_uniques

    @cython.boundscheck(False)
    def unique(self, ndarray[int64_t, ndim=1] values):
        if values.flags.writeable:
          # If the value is writeable (mutable) then use memview
          return self.unique_memview(values)

        # We cannot use the memoryview version on readonly-buffers due to
        # a limitation of Cython's typed memoryviews. Instead we can use
        # the slightly slower Cython ndarray type directly.
        # see https://github.com/cython/cython/issues/1605
        cdef:
           Py_ssize_t i, n = len(values)
           int ret = 0
           int64_t val
           khiter_t k
           bint seen_na = 0
           Int64Vector uniques = Int64Vector()
           Int64VectorData *ud

        ud = uniques.data

        with nogil:
            for i in range(n):
                val = values[i]
                IF False:
                  if val == val:
                      k = kh_get_int64(self.table, val)
                      if k == self.table.n_buckets:
                          kh_put_int64(self.table, val, &ret)
                          if needs_resize(ud):
                              with gil:
                                  uniques.resize()
                          append_data_int64(ud, val)
                  elif not seen_na:
                      seen_na = 1
                      if needs_resize(ud):
                          with gil:
                              uniques.resize()
                      append_data_int64(ud, NAN)
                ELSE:
                  k = kh_get_int64(self.table, val)
                  if k == self.table.n_buckets:
                      kh_put_int64(self.table, val, &ret)
                      if needs_resize(ud):
                          with gil:
                              uniques.resize()
                      append_data_int64(ud, val)
        return uniques.to_array()
      

    @cython.boundscheck(False)
    def unique_memview(self, int64_t[:] values):
        cdef:
           Py_ssize_t i, n = len(values)
           int ret = 0
           int64_t val
           khiter_t k
           bint seen_na = 0
           Int64Vector uniques = Int64Vector()
           Int64VectorData *ud

        ud = uniques.data

        with nogil:
            for i in range(n):
                val = values[i]
                IF False:
                  if val == val:
                      k = kh_get_int64(self.table, val)
                      if k == self.table.n_buckets:
                          kh_put_int64(self.table, val, &ret)
                          if needs_resize(ud):
                              with gil:
                                  uniques.resize()
                          append_data_int64(ud, val)
                  elif not seen_na:
                      seen_na = 1
                      if needs_resize(ud):
                          with gil:
                              uniques.resize()
                      append_data_int64(ud, NAN)
                ELSE:
                  k = kh_get_int64(self.table, val)
                  if k == self.table.n_buckets:
                      kh_put_int64(self.table, val, &ret)
                      if needs_resize(ud):
                          with gil:
                              uniques.resize()
                      append_data_int64(ud, val)
        return uniques.to_array()
      


cdef class StringHashTable(HashTable):
    # these by-definition *must* be strings
    # or a sentinel np.nan / None missing value
    na_string_sentinel = '__nan__'

    def __init__(self, int size_hint=1):
        self.table = kh_init_str()
        if size_hint is not None:
            kh_resize_str(self.table, size_hint)

    def __dealloc__(self):
        if self.table is not NULL:
            kh_destroy_str(self.table)
            self.table = NULL

    def sizeof(self, deep=False):
        """ return the size of my table in bytes """
        return self.table.n_buckets * (sizeof(char *) + # keys
                                       sizeof(size_t) + # vals
                                       sizeof(uint32_t)) # flags

    cpdef get_item(self, object val):
        cdef:
            khiter_t k
            char *v
        v = util.get_c_string(val)

        k = kh_get_str(self.table, v)
        if k != self.table.n_buckets:
            return self.table.vals[k]
        else:
            raise KeyError(val)

    cpdef set_item(self, object key, Py_ssize_t val):
        cdef:
            khiter_t k
            int ret = 0
            char *v

        v = util.get_c_string(val)

        k = kh_put_str(self.table, v, &ret)
        self.table.keys[k] = key
        if kh_exist_str(self.table, k):
            self.table.vals[k] = val
        else:
            raise KeyError(key)

    @cython.boundscheck(False)
    def get_indexer(self, ndarray[object] values):
        cdef:
            Py_ssize_t i, n = len(values)
            ndarray[int64_t] labels = np.empty(n, dtype=np.int64)
            int64_t *resbuf = <int64_t*> labels.data
            khiter_t k
            kh_str_t *table = self.table
            char *v
            char **vecs

        vecs = <char **> malloc(n * sizeof(char *))
        for i in range(n):
            val = values[i]
            v = util.get_c_string(val)
            vecs[i] = v

        with nogil:
            for i in range(n):
                k = kh_get_str(table, vecs[i])
                if k != table.n_buckets:
                    resbuf[i] = table.vals[k]
                else:
                    resbuf[i] = -1

        free(vecs)
        return labels

    @cython.boundscheck(False)
    def unique(self, ndarray[object] values):
        cdef:
            Py_ssize_t i, count, n = len(values)
            int64_t[:] uindexer
            int ret = 0
            object val
            ObjectVector uniques
            khiter_t k
            char *v
            char **vecs

        vecs = <char **> malloc(n * sizeof(char *))
        uindexer = np.empty(n, dtype=np.int64)
        for i in range(n):
            val = values[i]
            v = util.get_c_string(val)
            vecs[i] = v

        count = 0
        with nogil:
            for i in range(n):
                v = vecs[i]
                k = kh_get_str(self.table, v)
                if k == self.table.n_buckets:
                    kh_put_str(self.table, v, &ret)
                    uindexer[count] = i
                    count += 1
        free(vecs)

        # uniques
        uniques = ObjectVector()
        for i in range(count):
            uniques.append(values[uindexer[i]])
        return uniques.to_array()

    def factorize(self, ndarray[object] values):
        uniques = ObjectVector()
        labels = self.get_labels(values, uniques, 0, 0)
        return uniques.to_array(), labels

    @cython.boundscheck(False)
    def lookup(self, ndarray[object] values):
        cdef:
            Py_ssize_t i, n = len(values)
            int ret = 0
            object val
            char *v
            khiter_t k
            int64_t[:] locs = np.empty(n, dtype=np.int64)

        # these by-definition *must* be strings
        vecs = <char **> malloc(n * sizeof(char *))
        for i in range(n):
            val = values[i]

            if PyUnicode_Check(val) or PyString_Check(val):
                v = util.get_c_string(val)
            else:
                v = util.get_c_string(self.na_string_sentinel)
            vecs[i] = v

        with nogil:
            for i in range(n):
                v = vecs[i]
                k = kh_get_str(self.table, v)
                if k != self.table.n_buckets:
                    locs[i] = self.table.vals[k]
                else:
                    locs[i] = -1

        free(vecs)
        return np.asarray(locs)

    @cython.boundscheck(False)
    def map_locations(self, ndarray[object] values):
        cdef:
            Py_ssize_t i, n = len(values)
            int ret = 0
            object val
            char *v
            char **vecs
            khiter_t k

        # these by-definition *must* be strings
        vecs = <char **> malloc(n * sizeof(char *))
        for i in range(n):
            val = values[i]

            if PyUnicode_Check(val) or PyString_Check(val):
                v = util.get_c_string(val)
            else:
                v = util.get_c_string(self.na_string_sentinel)
            vecs[i] = v

        with nogil:
            for i in range(n):
                v = vecs[i]
                k = kh_put_str(self.table, v, &ret)
                self.table.vals[k] = i
        free(vecs)

    @cython.boundscheck(False)
    def get_labels(self, ndarray[object] values, ObjectVector uniques,
                   Py_ssize_t count_prior, int64_t na_sentinel,
                   bint check_null=1):
        cdef:
            Py_ssize_t i, n = len(values)
            int64_t[:] labels
            int64_t[:] uindexer
            Py_ssize_t idx, count = count_prior
            int ret = 0
            object val
            char *v
            char **vecs
            khiter_t k

        # these by-definition *must* be strings
        labels = np.zeros(n, dtype=np.int64)
        uindexer = np.empty(n, dtype=np.int64)

        # pre-filter out missing
        # and assign pointers
        vecs = <char **> malloc(n * sizeof(char *))
        for i in range(n):
            val = values[i]

            if PyUnicode_Check(val) or PyString_Check(val):
                v = util.get_c_string(val)
                vecs[i] = v
            else:
                labels[i] = na_sentinel

        # compute
        with nogil:
            for i in range(n):
                if labels[i] == na_sentinel:
                    continue

                v = vecs[i]
                k = kh_get_str(self.table, v)
                if k != self.table.n_buckets:
                    idx = self.table.vals[k]
                    labels[i] = <int64_t>idx
                else:
                    k = kh_put_str(self.table, v, &ret)
                    self.table.vals[k] = count
                    uindexer[count] = i
                    labels[i] = <int64_t>count
                    count += 1

        free(vecs)

        # uniques
        for i in range(count):
            uniques.append(values[uindexer[i]])

        return np.asarray(labels)

na_sentinel = object

cdef class PyObjectHashTable(HashTable):

    def __init__(self, size_hint=1):
        self.table = kh_init_pymap()
        kh_resize_pymap(self.table, size_hint)

    def __dealloc__(self):
        if self.table is not NULL:
            kh_destroy_pymap(self.table)
            self.table = NULL

    def __len__(self):
        return self.table.size

    def __contains__(self, object key):
        cdef khiter_t k
        hash(key)
        if key != key or key is None:
            key = na_sentinel
        k = kh_get_pymap(self.table, <PyObject*>key)
        return k != self.table.n_buckets

    def sizeof(self, deep=False):
        """ return the size of my table in bytes """
        return self.table.n_buckets * (sizeof(PyObject *) + # keys
                                       sizeof(size_t) + # vals
                                       sizeof(uint32_t)) # flags

    cpdef get_item(self, object val):
        cdef khiter_t k
        if val != val or val is None:
            val = na_sentinel
        k = kh_get_pymap(self.table, <PyObject*>val)
        if k != self.table.n_buckets:
            return self.table.vals[k]
        else:
            raise KeyError(val)

    cpdef set_item(self, object key, Py_ssize_t val):
        cdef:
            khiter_t k
            int ret = 0
            char* buf

        hash(key)
        if key != key or key is None:
            key = na_sentinel
        k = kh_put_pymap(self.table, <PyObject*>key, &ret)
        # self.table.keys[k] = key
        if kh_exist_pymap(self.table, k):
            self.table.vals[k] = val
        else:
            raise KeyError(key)

    def map_locations(self, ndarray[object] values):
        cdef:
            Py_ssize_t i, n = len(values)
            int ret = 0
            object val
            khiter_t k

        for i in range(n):
            val = values[i]
            hash(val)
            if val != val or val is None:
                val = na_sentinel

            k = kh_put_pymap(self.table, <PyObject*>val, &ret)
            self.table.vals[k] = i

    def lookup(self, ndarray[object] values):
        cdef:
            Py_ssize_t i, n = len(values)
            int ret = 0
            object val
            khiter_t k
            int64_t[:] locs = np.empty(n, dtype=np.int64)

        for i in range(n):
            val = values[i]
            hash(val)
            if val != val or val is None:
                val = na_sentinel

            k = kh_get_pymap(self.table, <PyObject*>val)
            if k != self.table.n_buckets:
                locs[i] = self.table.vals[k]
            else:
                locs[i] = -1

        return np.asarray(locs)

    def unique(self, ndarray[object] values):
        cdef:
            Py_ssize_t i, n = len(values)
            int ret = 0
            object val
            khiter_t k
            ObjectVector uniques = ObjectVector()
            bint seen_na = 0

        for i in range(n):
            val = values[i]
            hash(val)
            if not _checknan(val):
                k = kh_get_pymap(self.table, <PyObject*>val)
                if k == self.table.n_buckets:
                    kh_put_pymap(self.table, <PyObject*>val, &ret)
                    uniques.append(val)
            elif not seen_na:
                seen_na = 1
                uniques.append(nan)

        return uniques.to_array()

    def get_labels(self, ndarray[object] values, ObjectVector uniques,
                   Py_ssize_t count_prior, int64_t na_sentinel,
                   bint check_null=True):
        cdef:
            Py_ssize_t i, n = len(values)
            int64_t[:] labels
            Py_ssize_t idx, count = count_prior
            int ret = 0
            object val
            khiter_t k

        labels = np.empty(n, dtype=np.int64)

        for i in range(n):
            val = values[i]
            hash(val)

            if check_null and val != val or val is None:
                labels[i] = na_sentinel
                continue

            k = kh_get_pymap(self.table, <PyObject*>val)
            if k != self.table.n_buckets:
                idx = self.table.vals[k]
                labels[i] = idx
            else:
                k = kh_put_pymap(self.table, <PyObject*>val, &ret)
                self.table.vals[k] = count
                uniques.append(val)
                labels[i] = count
                count += 1

        return np.asarray(labels)
