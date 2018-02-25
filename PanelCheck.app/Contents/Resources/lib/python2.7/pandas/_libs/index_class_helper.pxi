"""
Template for functions of IndexEngine subclasses.

WARNING: DO NOT edit .pxi FILE directly, .pxi is generated from .pxi.in
"""

#----------------------------------------------------------------------
# IndexEngine Subclass Methods
#----------------------------------------------------------------------


cdef class Float64Engine(IndexEngine):

    def _call_monotonic(self, values):
        return algos.is_monotonic_float64(values, timelike=False)

    def get_backfill_indexer(self, other, limit=None):
        return algos.backfill_float64(self._get_index_values(),
                                        other, limit=limit)

    def get_pad_indexer(self, other, limit=None):
        return algos.pad_float64(self._get_index_values(),
                                   other, limit=limit)

    cdef _make_hash_table(self, n):
        return _hash.Float64HashTable(n)
    cdef _get_index_values(self):
        return algos.ensure_float64(self.vgetter())

    cdef _maybe_get_bool_indexer(self, object val):
        cdef:
            ndarray[uint8_t, cast=True] indexer
            ndarray[float64_t] values
            int count = 0
            Py_ssize_t i, n
            int last_true


        values = self._get_index_values_for_bool_indexer()
        n = len(values)

        result = np.empty(n, dtype=bool)
        indexer = result.view(np.uint8)

        for i in range(n):
            if values[i] == val:
                count += 1
                indexer[i] = 1
                last_true = i
            else:
                indexer[i] = 0

        if count == 0:
            raise KeyError(val)
        if count == 1:
            return last_true

        return result

    cdef _get_index_values_for_bool_indexer(self):
        return self._get_index_values()


cdef class UInt64Engine(IndexEngine):

    def _call_monotonic(self, values):
        return algos.is_monotonic_uint64(values, timelike=False)

    def get_backfill_indexer(self, other, limit=None):
        return algos.backfill_uint64(self._get_index_values(),
                                        other, limit=limit)

    def get_pad_indexer(self, other, limit=None):
        return algos.pad_uint64(self._get_index_values(),
                                   other, limit=limit)

    cdef _make_hash_table(self, n):
        return _hash.UInt64HashTable(n)
    cdef _check_type(self, object val):
        hash(val)
        if util.is_bool_object(val):
            raise KeyError(val)
        elif util.is_float_object(val):
            raise KeyError(val)
    cdef _get_index_values(self):
        return algos.ensure_uint64(self.vgetter())

    cdef _maybe_get_bool_indexer(self, object val):
        cdef:
            ndarray[uint8_t, cast=True] indexer
            ndarray[uint64_t] values
            int count = 0
            Py_ssize_t i, n
            int last_true

        if not util.is_integer_object(val):
            raise KeyError(val)

        values = self._get_index_values_for_bool_indexer()
        n = len(values)

        result = np.empty(n, dtype=bool)
        indexer = result.view(np.uint8)

        for i in range(n):
            if values[i] == val:
                count += 1
                indexer[i] = 1
                last_true = i
            else:
                indexer[i] = 0

        if count == 0:
            raise KeyError(val)
        if count == 1:
            return last_true

        return result

    cdef _get_index_values_for_bool_indexer(self):
        return self._get_index_values()


cdef class Int64Engine(IndexEngine):

    def _call_monotonic(self, values):
        return algos.is_monotonic_int64(values, timelike=False)

    def get_backfill_indexer(self, other, limit=None):
        return algos.backfill_int64(self._get_index_values(),
                                        other, limit=limit)

    def get_pad_indexer(self, other, limit=None):
        return algos.pad_int64(self._get_index_values(),
                                   other, limit=limit)

    cdef _make_hash_table(self, n):
        return _hash.Int64HashTable(n)
    cdef _check_type(self, object val):
        hash(val)
        if util.is_bool_object(val):
            raise KeyError(val)
        elif util.is_float_object(val):
            raise KeyError(val)
    cdef _get_index_values(self):
        return algos.ensure_int64(self.vgetter())

    cdef _maybe_get_bool_indexer(self, object val):
        cdef:
            ndarray[uint8_t, cast=True] indexer
            ndarray[int64_t] values
            int count = 0
            Py_ssize_t i, n
            int last_true

        if not util.is_integer_object(val):
            raise KeyError(val)

        values = self._get_index_values_for_bool_indexer()
        n = len(values)

        result = np.empty(n, dtype=bool)
        indexer = result.view(np.uint8)

        for i in range(n):
            if values[i] == val:
                count += 1
                indexer[i] = 1
                last_true = i
            else:
                indexer[i] = 0

        if count == 0:
            raise KeyError(val)
        if count == 1:
            return last_true

        return result

    cdef _get_index_values_for_bool_indexer(self):
        return self._get_index_values()


cdef class ObjectEngine(IndexEngine):

    def _call_monotonic(self, values):
        return algos.is_monotonic_object(values, timelike=False)

    def get_backfill_indexer(self, other, limit=None):
        return algos.backfill_object(self._get_index_values(),
                                        other, limit=limit)

    def get_pad_indexer(self, other, limit=None):
        return algos.pad_object(self._get_index_values(),
                                   other, limit=limit)

    cdef _make_hash_table(self, n):
        return _hash.PyObjectHashTable(n)
