# -*- coding: utf-8 -*-
# cython: profile=False

cimport cython
from cython cimport Py_ssize_t

import numpy as np
cimport numpy as cnp
from numpy cimport int64_t, int32_t, ndarray
cnp.import_array()

import pytz

# stdlib datetime imports
from datetime import time as datetime_time
from cpython.datetime cimport (datetime, tzinfo,
                               PyDateTime_Check, PyDate_Check,
                               PyDateTime_CheckExact, PyDateTime_IMPORT)
PyDateTime_IMPORT

from np_datetime cimport (check_dts_bounds,
                          pandas_datetimestruct,
                          pandas_datetime_to_datetimestruct, _string_to_dts,
                          PANDAS_DATETIMEUNIT, PANDAS_FR_ns,
                          npy_datetime,
                          dt64_to_dtstruct, dtstruct_to_dt64,
                          get_datetime64_unit, get_datetime64_value,
                          pydatetime_to_dt64)
from np_datetime import OutOfBoundsDatetime

from util cimport (is_string_object,
                   is_datetime64_object,
                   is_integer_object, is_float_object, is_array)

from timedeltas cimport cast_from_unit
from timezones cimport (is_utc, is_tzlocal, is_fixed_offset,
                        treat_tz_as_dateutil, treat_tz_as_pytz,
                        get_utcoffset, get_dst_info,
                        get_timezone, maybe_get_tz, tz_compare)
from parsing import parse_datetime_string

from nattype import nat_strings, NaT
from nattype cimport NPY_NAT, checknull_with_nat

# ----------------------------------------------------------------------
# Constants

cdef int64_t DAY_NS = 86400000000000LL
NS_DTYPE = np.dtype('M8[ns]')
TD_DTYPE = np.dtype('m8[ns]')

UTC = pytz.UTC

# ----------------------------------------------------------------------
# Misc Helpers

# TODO: How to declare np.datetime64 as the input type?
cdef inline int64_t get_datetime64_nanos(object val) except? -1:
    """
    Extract the value and unit from a np.datetime64 object, then convert the
    value to nanoseconds if necessary.
    """
    cdef:
        pandas_datetimestruct dts
        PANDAS_DATETIMEUNIT unit
        npy_datetime ival

    unit = get_datetime64_unit(val)
    ival = get_datetime64_value(val)

    if unit != PANDAS_FR_ns:
        pandas_datetime_to_datetimestruct(ival, unit, &dts)
        check_dts_bounds(&dts)
        ival = dtstruct_to_dt64(&dts)

    return ival


def ensure_datetime64ns(ndarray arr, copy=True):
    """
    Ensure a np.datetime64 array has dtype specifically 'datetime64[ns]'

    Parameters
    ----------
    arr : ndarray
    copy : boolean, default True

    Returns
    -------
    result : ndarray with dtype datetime64[ns]

    """
    cdef:
        Py_ssize_t i, n = arr.size
        ndarray[int64_t] ivalues, iresult
        PANDAS_DATETIMEUNIT unit
        pandas_datetimestruct dts

    shape = (<object> arr).shape

    ivalues = arr.view(np.int64).ravel()

    result = np.empty(shape, dtype='M8[ns]')
    iresult = result.ravel().view(np.int64)

    if len(iresult) == 0:
        return result

    unit = get_datetime64_unit(arr.flat[0])
    if unit == PANDAS_FR_ns:
        if copy:
            arr = arr.copy()
        result = arr
    else:
        for i in range(n):
            if ivalues[i] != NPY_NAT:
                pandas_datetime_to_datetimestruct(ivalues[i], unit, &dts)
                iresult[i] = dtstruct_to_dt64(&dts)
                check_dts_bounds(&dts)
            else:
                iresult[i] = NPY_NAT

    return result


def ensure_timedelta64ns(ndarray arr, copy=True):
    """
    Ensure a np.timedelta64 array has dtype specifically 'timedelta64[ns]'

    Parameters
    ----------
    arr : ndarray
    copy : boolean, default True

    Returns
    -------
    result : ndarray with dtype timedelta64[ns]

    """
    return arr.astype(TD_DTYPE, copy=copy)


def datetime_to_datetime64(ndarray[object] values):
    """
    Convert ndarray of datetime-like objects to int64 array representing
    nanosecond timestamps.

    Parameters
    ----------
    values : ndarray

    Returns
    -------
    result : ndarray with dtype int64
    inferred_tz : tzinfo or None
    """
    cdef:
        Py_ssize_t i, n = len(values)
        object val, inferred_tz = None
        ndarray[int64_t] iresult
        pandas_datetimestruct dts
        _TSObject _ts

    result = np.empty(n, dtype='M8[ns]')
    iresult = result.view('i8')
    for i in range(n):
        val = values[i]
        if checknull_with_nat(val):
            iresult[i] = NPY_NAT
        elif PyDateTime_Check(val):
            if val.tzinfo is not None:
                if inferred_tz is not None:
                    if not tz_compare(val.tzinfo, inferred_tz):
                        raise ValueError('Array must be all same time zone')
                else:
                    inferred_tz = get_timezone(val.tzinfo)

                _ts = convert_datetime_to_tsobject(val, None)
                iresult[i] = _ts.value
                check_dts_bounds(&_ts.dts)
            else:
                if inferred_tz is not None:
                    raise ValueError('Cannot mix tz-aware with '
                                     'tz-naive values')
                iresult[i] = pydatetime_to_dt64(val, &dts)
                check_dts_bounds(&dts)
        else:
            raise TypeError('Unrecognized value type: %s' % type(val))

    return result, inferred_tz


cdef inline maybe_datetimelike_to_i8(object val):
    """
    Try to convert to a nanosecond timestamp.  Fall back to returning the
    input value.

    Parameters
    ----------
    val : object

    Returns
    -------
    val : int64 timestamp or original input
    """
    cdef:
        pandas_datetimestruct dts
    try:
        return val.value
    except AttributeError:
        if is_datetime64_object(val):
            return get_datetime64_value(val)
        elif PyDateTime_Check(val):
            return convert_datetime_to_tsobject(val, None).value
        return val


# ----------------------------------------------------------------------
# _TSObject Conversion

# lightweight C object to hold datetime & int64 pair
cdef class _TSObject:
    # cdef:
    #    pandas_datetimestruct dts      # pandas_datetimestruct
    #    int64_t value               # numpy dt64
    #    object tzinfo

    @property
    def value(self):
        return self.value


cpdef int64_t pydt_to_i8(object pydt) except? -1:
    """
    Convert to int64 representation compatible with numpy datetime64; converts
    to UTC

    Parameters
    ----------
    pydt : object

    Returns
    -------
    i8value : np.int64
    """
    cdef:
        _TSObject ts

    ts = convert_to_tsobject(pydt, None, None, 0, 0)

    return ts.value


cdef convert_to_tsobject(object ts, object tz, object unit,
                         bint dayfirst, bint yearfirst):
    """
    Extract datetime and int64 from any of:
        - np.int64 (with unit providing a possible modifier)
        - np.datetime64
        - a float (with unit providing a possible modifier)
        - python int or long object (with unit providing a possible modifier)
        - iso8601 string object
        - python datetime object
        - another timestamp object
    """
    cdef:
        _TSObject obj

    if tz is not None:
        tz = maybe_get_tz(tz)

    obj = _TSObject()

    if is_string_object(ts):
        return convert_str_to_tsobject(ts, tz, unit, dayfirst, yearfirst)

    if ts is None or ts is NaT:
        obj.value = NPY_NAT
    elif is_datetime64_object(ts):
        if ts.view('i8') == NPY_NAT:
            obj.value = NPY_NAT
        else:
            obj.value = get_datetime64_nanos(ts)
            dt64_to_dtstruct(obj.value, &obj.dts)
    elif is_integer_object(ts):
        if ts == NPY_NAT:
            obj.value = NPY_NAT
        else:
            ts = ts * cast_from_unit(None, unit)
            obj.value = ts
            dt64_to_dtstruct(ts, &obj.dts)
    elif is_float_object(ts):
        if ts != ts or ts == NPY_NAT:
            obj.value = NPY_NAT
        else:
            ts = cast_from_unit(ts, unit)
            obj.value = ts
            dt64_to_dtstruct(ts, &obj.dts)
    elif PyDateTime_Check(ts):
        return convert_datetime_to_tsobject(ts, tz)
    elif PyDate_Check(ts):
        # Keep the converter same as PyDateTime's
        ts = datetime.combine(ts, datetime_time())
        return convert_datetime_to_tsobject(ts, tz)
    elif getattr(ts, '_typ', None) == 'period':
        raise ValueError("Cannot convert Period to Timestamp "
                         "unambiguously. Use to_timestamp")
    else:
        raise TypeError('Cannot convert input [{}] of type {} to '
                        'Timestamp'.format(ts, type(ts)))

    if tz is not None:
        localize_tso(obj, tz)

    if obj.value != NPY_NAT:
        # check_overflows needs to run after localize_tso
        check_dts_bounds(&obj.dts)
        check_overflows(obj)
    return obj


cdef _TSObject convert_datetime_to_tsobject(datetime ts, object tz,
                                            int32_t nanos=0):
    """
    Convert a datetime (or Timestamp) input `ts`, along with optional timezone
    object `tz` to a _TSObject.

    The optional argument `nanos` allows for cases where datetime input
    needs to be supplemented with higher-precision information.

    Parameters
    ----------
    ts : datetime or Timestamp
        Value to be converted to _TSObject
    tz : tzinfo or None
        timezone for the timezone-aware output
    nanos : int32_t, default is 0
        nanoseconds supplement the precision of the datetime input ts

    Returns
    -------
    obj : _TSObject
    """
    cdef:
        _TSObject obj = _TSObject()

    if tz is not None:
        tz = maybe_get_tz(tz)

        # sort of a temporary hack
        if ts.tzinfo is not None:
            if hasattr(tz, 'normalize') and hasattr(ts.tzinfo, '_utcoffset'):
                ts = tz.normalize(ts)
                obj.value = pydatetime_to_dt64(ts, &obj.dts)
                obj.tzinfo = ts.tzinfo
            else:
                # tzoffset
                try:
                    tz = ts.astimezone(tz).tzinfo
                except:
                    pass
                obj.value = pydatetime_to_dt64(ts, &obj.dts)
                ts_offset = get_utcoffset(ts.tzinfo, ts)
                obj.value -= int(ts_offset.total_seconds() * 1e9)
                tz_offset = get_utcoffset(tz, ts)
                obj.value += int(tz_offset.total_seconds() * 1e9)
                dt64_to_dtstruct(obj.value, &obj.dts)
                obj.tzinfo = tz
        elif not is_utc(tz):
            ts = _localize_pydatetime(ts, tz)
            obj.value = pydatetime_to_dt64(ts, &obj.dts)
            obj.tzinfo = ts.tzinfo
        else:
            # UTC
            obj.value = pydatetime_to_dt64(ts, &obj.dts)
            obj.tzinfo = pytz.utc
    else:
        obj.value = pydatetime_to_dt64(ts, &obj.dts)
        obj.tzinfo = ts.tzinfo

    if obj.tzinfo is not None and not is_utc(obj.tzinfo):
        offset = get_utcoffset(obj.tzinfo, ts)
        obj.value -= int(offset.total_seconds() * 1e9)

    if not PyDateTime_CheckExact(ts):
        # datetime instance but not datetime type --> Timestamp
        obj.value += ts.nanosecond
        obj.dts.ps = ts.nanosecond * 1000

    if nanos:
        obj.value += nanos
        obj.dts.ps = nanos * 1000

    check_dts_bounds(&obj.dts)
    check_overflows(obj)
    return obj


cdef _TSObject convert_str_to_tsobject(object ts, object tz, object unit,
                                       bint dayfirst=False,
                                       bint yearfirst=False):
    """
    Convert a string-like (bytes or unicode) input `ts`, along with optional
    timezone object `tz` to a _TSObject.

    The optional arguments `dayfirst` and `yearfirst` are passed to the
    dateutil parser.

    Parameters
    ----------
    ts : bytes or unicode
        Value to be converted to _TSObject
    tz : tzinfo or None
        timezone for the timezone-aware output
    dayfirst : bool, default False
        When parsing an ambiguous date string, interpret e.g. "3/4/1975" as
        April 3, as opposed to the standard US interpretation March 4.
    yearfirst : bool, default False
        When parsing an ambiguous date string, interpret e.g. "01/05/09"
        as "May 9, 2001", as opposed to the default "Jan 5, 2009"

    Returns
    -------
    obj : _TSObject
    """
    cdef:
        _TSObject obj
        int out_local = 0, out_tzoffset = 0
        datetime dt

    if tz is not None:
        tz = maybe_get_tz(tz)

    obj = _TSObject()

    assert is_string_object(ts)

    if len(ts) == 0 or ts in nat_strings:
        ts = NaT
    elif ts == 'now':
        # Issue 9000, we short-circuit rather than going
        # into np_datetime_strings which returns utc
        ts = datetime.now(tz)
    elif ts == 'today':
        # Issue 9000, we short-circuit rather than going
        # into np_datetime_strings which returns a normalized datetime
        ts = datetime.now(tz)
        # equiv: datetime.today().replace(tzinfo=tz)
    else:
        try:
            _string_to_dts(ts, &obj.dts, &out_local, &out_tzoffset)
            obj.value = dtstruct_to_dt64(&obj.dts)
            check_dts_bounds(&obj.dts)
            if out_local == 1:
                obj.tzinfo = pytz.FixedOffset(out_tzoffset)
                obj.value = tz_convert_single(obj.value, obj.tzinfo, 'UTC')
                if tz is None:
                    check_dts_bounds(&obj.dts)
                    check_overflows(obj)
                    return obj
                else:
                    # Keep the converter same as PyDateTime's
                    obj = convert_to_tsobject(obj.value, obj.tzinfo,
                                              None, 0, 0)
                    dt = datetime(obj.dts.year, obj.dts.month, obj.dts.day,
                                  obj.dts.hour, obj.dts.min, obj.dts.sec,
                                  obj.dts.us, obj.tzinfo)
                    obj = convert_datetime_to_tsobject(dt, tz,
                                                       nanos=obj.dts.ps / 1000)
                    return obj

            else:
                ts = obj.value
                if tz is not None:
                    # shift for localize_tso
                    ts = tz_localize_to_utc(np.array([ts], dtype='i8'), tz,
                                            ambiguous='raise',
                                            errors='raise')[0]

        except OutOfBoundsDatetime:
            # GH#19382 for just-barely-OutOfBounds falling back to dateutil
            # parser will return incorrect result because it will ignore
            # nanoseconds
            raise

        except ValueError:
            try:
                ts = parse_datetime_string(ts, dayfirst=dayfirst,
                                           yearfirst=yearfirst)
            except Exception:
                raise ValueError("could not convert string to Timestamp")

    return convert_to_tsobject(ts, tz, unit, dayfirst, yearfirst)


cdef inline check_overflows(_TSObject obj):
    """
    Check that we haven't silently overflowed in timezone conversion
    
    Parameters
    ----------
    obj : _TSObject

    Returns
    -------
    None

    Raises
    ------
    OutOfBoundsDatetime
    """
    # GH#12677
    if obj.dts.year == 1677:
        if not (obj.value < 0):
            raise OutOfBoundsDatetime
    elif obj.dts.year == 2262:
        if not (obj.value > 0):
            raise OutOfBoundsDatetime


# ----------------------------------------------------------------------
# Localization

cdef inline void localize_tso(_TSObject obj, tzinfo tz):
    """
    Given the UTC nanosecond timestamp in obj.value, find the wall-clock
    representation of that timestamp in the given timezone.

    Parameters
    ----------
    obj : _TSObject
    tz : tzinfo

    Returns
    -------
    None

    Notes
    -----
    Sets obj.tzinfo inplace, alters obj.dts inplace.
    """
    cdef:
        ndarray[int64_t] trans, deltas
        int64_t delta, local_val
        Py_ssize_t posn
        datetime dt

    assert obj.tzinfo is None

    if is_utc(tz):
        pass
    elif obj.value == NPY_NAT:
        pass
    elif is_tzlocal(tz):
        local_val = tz_convert_utc_to_tzlocal(obj.value, tz)
        dt64_to_dtstruct(local_val, &obj.dts)
    else:
        # Adjust datetime64 timestamp, recompute datetimestruct
        trans, deltas, typ = get_dst_info(tz)

        pos = trans.searchsorted(obj.value, side='right') - 1

        # static/pytz/dateutil specific code
        if is_fixed_offset(tz):
            # statictzinfo
            assert len(deltas) == 1, len(deltas)
            dt64_to_dtstruct(obj.value + deltas[0], &obj.dts)
        elif treat_tz_as_pytz(tz):
            tz = tz._tzinfos[tz._transition_info[pos]]
            dt64_to_dtstruct(obj.value + deltas[pos], &obj.dts)
        elif treat_tz_as_dateutil(tz):
            dt64_to_dtstruct(obj.value + deltas[pos], &obj.dts)
        else:
            pass

    obj.tzinfo = tz


cdef inline datetime _localize_pydatetime(datetime dt, tzinfo tz):
    """
    Take a datetime/Timestamp in UTC and localizes to timezone tz.

    NB: Unlike the version in tslib, this treats datetime and Timestamp objects
        identically, i.e. discards nanos from Timestamps.
        It also assumes that the `tz` input is not None.
    """
    if tz == 'UTC' or tz is UTC:
        return UTC.localize(dt)
    try:
        # datetime.replace with pytz may be incorrect result
        return tz.localize(dt)
    except AttributeError:
        return dt.replace(tzinfo=tz)

# ----------------------------------------------------------------------
# Timezone Conversion

cdef inline int64_t tz_convert_tzlocal_to_utc(int64_t val, tzinfo tz):
    """
    Parameters
    ----------
    val : int64_t
    tz : tzinfo

    Returns
    -------
    utc_date : int64_t

    See Also
    --------
    tz_convert_utc_to_tzlocal
    """
    cdef:
        pandas_datetimestruct dts
        int64_t utc_date, delta
        datetime dt

    dt64_to_dtstruct(val, &dts)
    dt = datetime(dts.year, dts.month, dts.day, dts.hour,
                  dts.min, dts.sec, dts.us, tz)
    delta = int(get_utcoffset(tz, dt).total_seconds()) * 1000000000
    utc_date = val - delta
    return utc_date


cdef inline int64_t tz_convert_utc_to_tzlocal(int64_t utc_val, tzinfo tz):
    """
    Parameters
    ----------
    utc_val : int64_t
    tz : tzinfo

    Returns
    -------
    local_val : int64_t

    See Also
    --------
    tz_convert_tzlocal_to_utc

    Notes
    -----
    The key difference between this and tz_convert_tzlocal_to_utc is a
    an addition flipped to a subtraction in the last line.
    """
    cdef:
        pandas_datetimestruct dts
        int64_t local_val, delta
        datetime dt

    dt64_to_dtstruct(utc_val, &dts)
    dt = datetime(dts.year, dts.month, dts.day, dts.hour,
                  dts.min, dts.sec, dts.us, tz)
    delta = int(get_utcoffset(tz, dt).total_seconds()) * 1000000000
    local_val = utc_val + delta
    return local_val


cpdef int64_t tz_convert_single(int64_t val, object tz1, object tz2):
    """
    Convert the val (in i8) from timezone1 to timezone2

    This is a single timezone version of tz_convert

    Parameters
    ----------
    val : int64
    tz1 : string / timezone object
    tz2 : string / timezone object

    Returns
    -------
    int64 converted

    """

    cdef:
        ndarray[int64_t] trans, deltas
        Py_ssize_t pos
        int64_t v, offset, utc_date
        pandas_datetimestruct dts
        datetime dt

    # See GH#17734 We should always be converting either from UTC or to UTC
    assert (is_utc(tz1) or tz1 == 'UTC') or (is_utc(tz2) or tz2 == 'UTC')

    if val == NPY_NAT:
        return val

    # Convert to UTC
    if is_tzlocal(tz1):
        utc_date = tz_convert_tzlocal_to_utc(val, tz1)
    elif get_timezone(tz1) != 'UTC':
        trans, deltas, typ = get_dst_info(tz1)
        pos = trans.searchsorted(val, side='right') - 1
        if pos < 0:
            raise ValueError('First time before start of DST info')
        offset = deltas[pos]
        utc_date = val - offset
    else:
        utc_date = val

    if get_timezone(tz2) == 'UTC':
        return utc_date
    elif is_tzlocal(tz2):
        return tz_convert_utc_to_tzlocal(utc_date, tz2)

    # Convert UTC to other timezone
    trans, deltas, typ = get_dst_info(tz2)

    pos = trans.searchsorted(utc_date, side='right') - 1
    if pos < 0:
        raise ValueError('First time before start of DST info')

    offset = deltas[pos]
    return utc_date + offset


@cython.boundscheck(False)
@cython.wraparound(False)
def tz_convert(ndarray[int64_t] vals, object tz1, object tz2):
    """
    Convert the values (in i8) from timezone1 to timezone2

    Parameters
    ----------
    vals : int64 ndarray
    tz1 : string / timezone object
    tz2 : string / timezone object

    Returns
    -------
    int64 ndarray of converted
    """

    cdef:
        ndarray[int64_t] utc_dates, tt, result, trans, deltas
        Py_ssize_t i, j, pos, n = len(vals)
        ndarray[Py_ssize_t] posn
        int64_t v, offset, delta
        pandas_datetimestruct dts
        datetime dt

    if len(vals) == 0:
        return np.array([], dtype=np.int64)

    # Convert to UTC
    if get_timezone(tz1) != 'UTC':
        utc_dates = np.empty(n, dtype=np.int64)
        if is_tzlocal(tz1):
            for i in range(n):
                v = vals[i]
                if v == NPY_NAT:
                    utc_dates[i] = NPY_NAT
                else:
                    utc_dates[i] = tz_convert_tzlocal_to_utc(v, tz1)
        else:
            trans, deltas, typ = get_dst_info(tz1)

            # all-NaT
            tt = vals[vals != NPY_NAT]
            if not len(tt):
                return vals

            posn = trans.searchsorted(tt, side='right')
            j = 0
            for i in range(n):
                v = vals[i]
                if v == NPY_NAT:
                    utc_dates[i] = NPY_NAT
                else:
                    pos = posn[j] - 1
                    j = j + 1
                    if pos < 0:
                        raise ValueError('First time before start of DST info')
                    offset = deltas[pos]
                    utc_dates[i] = v - offset
    else:
        utc_dates = vals

    if get_timezone(tz2) == 'UTC':
        return utc_dates

    result = np.zeros(n, dtype=np.int64)
    if is_tzlocal(tz2):
        for i in range(n):
            v = utc_dates[i]
            if v == NPY_NAT:
                result[i] = NPY_NAT
            else:
                result[i] = tz_convert_utc_to_tzlocal(v, tz2)
        return result

    # Convert UTC to other timezone
    trans, deltas, typ = get_dst_info(tz2)

    # use first non-NaT element
    # if all-NaT, return all-NaT
    if (result == NPY_NAT).all():
        return result

    # if all NaT, return all NaT
    tt = utc_dates[utc_dates!=NPY_NAT]
    if not len(tt):
        return utc_dates

    posn = trans.searchsorted(tt, side='right')

    j = 0
    for i in range(n):
        v = utc_dates[i]
        if vals[i] == NPY_NAT:
            result[i] = vals[i]
        else:
            pos = posn[j] - 1
            j = j + 1
            if pos < 0:
                raise ValueError('First time before start of DST info')
            offset = deltas[pos]
            result[i] = v + offset
    return result


# TODO: cdef scalar version to call from convert_str_to_tsobject
@cython.boundscheck(False)
@cython.wraparound(False)
def tz_localize_to_utc(ndarray[int64_t] vals, object tz, object ambiguous=None,
                       object errors='raise'):
    """
    Localize tzinfo-naive i8 to given time zone (using pytz). If
    there are ambiguities in the values, raise AmbiguousTimeError.

    Returns
    -------
    localized : DatetimeIndex
    """
    cdef:
        ndarray[int64_t] trans, deltas, idx_shifted
        ndarray ambiguous_array
        Py_ssize_t i, idx, pos, ntrans, n = len(vals)
        int64_t *tdata
        int64_t v, left, right
        ndarray[int64_t] result, result_a, result_b, dst_hours
        pandas_datetimestruct dts
        bint infer_dst = False, is_dst = False, fill = False
        bint is_coerce = errors == 'coerce', is_raise = errors == 'raise'
        datetime dt

    # Vectorized version of DstTzInfo.localize

    assert is_coerce or is_raise

    if tz == UTC or tz is None:
        return vals

    result = np.empty(n, dtype=np.int64)

    if is_tzlocal(tz):
        for i in range(n):
            v = vals[i]
            result[i] = tz_convert_tzlocal_to_utc(v, tz)
        return result

    if is_string_object(ambiguous):
        if ambiguous == 'infer':
            infer_dst = True
        elif ambiguous == 'NaT':
            fill = True
    elif isinstance(ambiguous, bool):
        is_dst = True
        if ambiguous:
            ambiguous_array = np.ones(len(vals), dtype=bool)
        else:
            ambiguous_array = np.zeros(len(vals), dtype=bool)
    elif hasattr(ambiguous, '__iter__'):
        is_dst = True
        if len(ambiguous) != len(vals):
            raise ValueError("Length of ambiguous bool-array must be "
                             "the same size as vals")
        ambiguous_array = np.asarray(ambiguous)

    trans, deltas, typ = get_dst_info(tz)

    tdata = <int64_t*> trans.data
    ntrans = len(trans)

    result_a = np.empty(n, dtype=np.int64)
    result_b = np.empty(n, dtype=np.int64)
    result_a.fill(NPY_NAT)
    result_b.fill(NPY_NAT)

    # left side
    idx_shifted = (np.maximum(0, trans.searchsorted(
        vals - DAY_NS, side='right') - 1)).astype(np.int64)

    for i in range(n):
        v = vals[i] - deltas[idx_shifted[i]]
        pos = bisect_right_i8(tdata, v, ntrans) - 1

        # timestamp falls to the left side of the DST transition
        if v + deltas[pos] == vals[i]:
            result_a[i] = v

    # right side
    idx_shifted = (np.maximum(0, trans.searchsorted(
        vals + DAY_NS, side='right') - 1)).astype(np.int64)

    for i in range(n):
        v = vals[i] - deltas[idx_shifted[i]]
        pos = bisect_right_i8(tdata, v, ntrans) - 1

        # timestamp falls to the right side of the DST transition
        if v + deltas[pos] == vals[i]:
            result_b[i] = v

    if infer_dst:
        dst_hours = np.empty(n, dtype=np.int64)
        dst_hours.fill(NPY_NAT)

        # Get the ambiguous hours (given the above, these are the hours
        # where result_a != result_b and neither of them are NAT)
        both_nat = np.logical_and(result_a != NPY_NAT, result_b != NPY_NAT)
        both_eq = result_a == result_b
        trans_idx = np.squeeze(np.nonzero(np.logical_and(both_nat, ~both_eq)))
        if trans_idx.size == 1:
            stamp = _render_tstamp(vals[trans_idx])
            raise pytz.AmbiguousTimeError(
                "Cannot infer dst time from %s as there "
                "are no repeated times" % stamp)
        # Split the array into contiguous chunks (where the difference between
        # indices is 1).  These are effectively dst transitions in different
        # years which is useful for checking that there is not an ambiguous
        # transition in an individual year.
        if trans_idx.size > 0:
            one_diff = np.where(np.diff(trans_idx) != 1)[0] +1
            trans_grp = np.array_split(trans_idx, one_diff)

            # Iterate through each day, if there are no hours where the
            # delta is negative (indicates a repeat of hour) the switch
            # cannot be inferred
            for grp in trans_grp:

                delta = np.diff(result_a[grp])
                if grp.size == 1 or np.all(delta > 0):
                    stamp = _render_tstamp(vals[grp[0]])
                    raise pytz.AmbiguousTimeError(stamp)

                # Find the index for the switch and pull from a for dst and b
                # for standard
                switch_idx = (delta <= 0).nonzero()[0]
                if switch_idx.size > 1:
                    raise pytz.AmbiguousTimeError(
                        "There are %i dst switches when "
                        "there should only be 1." % switch_idx.size)
                switch_idx = switch_idx[0] + 1
                # Pull the only index and adjust
                a_idx = grp[:switch_idx]
                b_idx = grp[switch_idx:]
                dst_hours[grp] = np.hstack((result_a[a_idx], result_b[b_idx]))

    for i in range(n):
        left = result_a[i]
        right = result_b[i]
        if vals[i] == NPY_NAT:
            result[i] = vals[i]
        elif left != NPY_NAT and right != NPY_NAT:
            if left == right:
                result[i] = left
            else:
                if infer_dst and dst_hours[i] != NPY_NAT:
                    result[i] = dst_hours[i]
                elif is_dst:
                    if ambiguous_array[i]:
                        result[i] = left
                    else:
                        result[i] = right
                elif fill:
                    result[i] = NPY_NAT
                else:
                    stamp = _render_tstamp(vals[i])
                    raise pytz.AmbiguousTimeError(
                        "Cannot infer dst time from %r, try using the "
                        "'ambiguous' argument" % stamp)
        elif left != NPY_NAT:
            result[i] = left
        elif right != NPY_NAT:
            result[i] = right
        else:
            if is_coerce:
                result[i] = NPY_NAT
            else:
                stamp = _render_tstamp(vals[i])
                raise pytz.NonExistentTimeError(stamp)

    return result


cdef inline bisect_right_i8(int64_t *data, int64_t val, Py_ssize_t n):
    cdef Py_ssize_t pivot, left = 0, right = n

    assert n >= 1

    # edge cases
    if val > data[n - 1]:
        return n

    if val < data[0]:
        return 0

    while left < right:
        pivot = left + (right - left) // 2

        if data[pivot] <= val:
            left = pivot + 1
        else:
            right = pivot

    return left


cdef inline str _render_tstamp(int64_t val):
    """ Helper function to render exception messages"""
    from pandas._libs.tslib import Timestamp
    return str(Timestamp(val))


# ----------------------------------------------------------------------
# Normalization

@cython.wraparound(False)
@cython.boundscheck(False)
def date_normalize(ndarray[int64_t] stamps, tz=None):
    """
    Normalize each of the (nanosecond) timestamps in the given array by
    rounding down to the beginning of the day (i.e. midnight).  If `tz`
    is not None, then this is midnight for this timezone.

    Parameters
    ----------
    stamps : int64 ndarray
    tz : tzinfo or None

    Returns
    -------
    result : int64 ndarray of converted of normalized nanosecond timestamps
    """
    cdef:
        Py_ssize_t i, n = len(stamps)
        pandas_datetimestruct dts
        ndarray[int64_t] result = np.empty(n, dtype=np.int64)

    if tz is not None:
        tz = maybe_get_tz(tz)
        result = _normalize_local(stamps, tz)
    else:
        with nogil:
            for i in range(n):
                if stamps[i] == NPY_NAT:
                    result[i] = NPY_NAT
                    continue
                dt64_to_dtstruct(stamps[i], &dts)
                result[i] = _normalized_stamp(&dts)

    return result


@cython.wraparound(False)
@cython.boundscheck(False)
cdef ndarray[int64_t] _normalize_local(ndarray[int64_t] stamps, object tz):
    """
    Normalize each of the (nanosecond) timestamps in the given array by
    rounding down to the beginning of the day (i.e. midnight) for the
    given timezone `tz`.

    Parameters
    ----------
    stamps : int64 ndarray
    tz : tzinfo or None

    Returns
    -------
    result : int64 ndarray of converted of normalized nanosecond timestamps
    """
    cdef:
        Py_ssize_t n = len(stamps)
        ndarray[int64_t] result = np.empty(n, dtype=np.int64)
        ndarray[int64_t] trans, deltas, pos
        pandas_datetimestruct dts
        datetime dt

    if is_utc(tz):
        with nogil:
            for i in range(n):
                if stamps[i] == NPY_NAT:
                    result[i] = NPY_NAT
                    continue
                dt64_to_dtstruct(stamps[i], &dts)
                result[i] = _normalized_stamp(&dts)
    elif is_tzlocal(tz):
        for i in range(n):
            if stamps[i] == NPY_NAT:
                result[i] = NPY_NAT
                continue
            local_val = tz_convert_utc_to_tzlocal(stamps[i], tz)
            dt64_to_dtstruct(local_val, &dts)
            result[i] = _normalized_stamp(&dts)
    else:
        # Adjust datetime64 timestamp, recompute datetimestruct
        trans, deltas, typ = get_dst_info(tz)

        _pos = trans.searchsorted(stamps, side='right') - 1
        if _pos.dtype != np.int64:
            _pos = _pos.astype(np.int64)
        pos = _pos

        # statictzinfo
        if typ not in ['pytz', 'dateutil']:
            for i in range(n):
                if stamps[i] == NPY_NAT:
                    result[i] = NPY_NAT
                    continue
                dt64_to_dtstruct(stamps[i] + deltas[0], &dts)
                result[i] = _normalized_stamp(&dts)
        else:
            for i in range(n):
                if stamps[i] == NPY_NAT:
                    result[i] = NPY_NAT
                    continue
                dt64_to_dtstruct(stamps[i] + deltas[pos[i]], &dts)
                result[i] = _normalized_stamp(&dts)

    return result


cdef inline int64_t _normalized_stamp(pandas_datetimestruct *dts) nogil:
    """
    Normalize the given datetimestruct to midnight, then convert to int64_t.

    Parameters
    ----------
    *dts : pointer to pandas_datetimestruct

    Returns
    -------
    stamp : int64
    """
    dts.hour = 0
    dts.min = 0
    dts.sec = 0
    dts.us = 0
    dts.ps = 0
    return dtstruct_to_dt64(dts)


def is_date_array_normalized(ndarray[int64_t] stamps, tz=None):
    """
    Check if all of the given (nanosecond) timestamps are normalized to
    midnight, i.e. hour == minute == second == 0.  If the optional timezone
    `tz` is not None, then this is midnight for this timezone.

    Parameters
    ----------
    stamps : int64 ndarray
    tz : tzinfo or None

    Returns
    -------
    is_normalized : bool True if all stamps are normalized
    """
    cdef:
        Py_ssize_t i, n = len(stamps)
        ndarray[int64_t] trans, deltas
        pandas_datetimestruct dts
        int64_t local_val

    if tz is None or is_utc(tz):
        for i in range(n):
            dt64_to_dtstruct(stamps[i], &dts)
            if (dts.hour + dts.min + dts.sec + dts.us) > 0:
                return False
    elif is_tzlocal(tz):
        for i in range(n):
            local_val = tz_convert_utc_to_tzlocal(stamps[i], tz)
            dt64_to_dtstruct(local_val, &dts)
            if (dts.hour + dts.min + dts.sec + dts.us) > 0:
                return False
    else:
        trans, deltas, typ = get_dst_info(tz)

        for i in range(n):
            # Adjust datetime64 timestamp, recompute datetimestruct
            pos = trans.searchsorted(stamps[i]) - 1
            inf = tz._transition_info[pos]

            dt64_to_dtstruct(stamps[i] + deltas[pos], &dts)
            if (dts.hour + dts.min + dts.sec + dts.us) > 0:
                return False

    return True
