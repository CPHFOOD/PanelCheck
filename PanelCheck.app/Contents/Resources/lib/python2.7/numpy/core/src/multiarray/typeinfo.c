/*
 * Provides namedtuples for numpy.core.multiarray.typeinfo
 * Unfortunately, we need two different types to cover the cases where min/max
 * do and do not appear in the tuple.
 */
#define PY_SSIZE_T_CLEAN
#include <Python.h>

/* In python 2, this is not exported from Python.h */
#include <structseq.h>

#define NPY_NO_DEPRECATED_API NPY_API_VERSION
#define _MULTIARRAYMODULE
#include "npy_pycompat.h"


PyTypeObject PyArray_typeinfoType;
PyTypeObject PyArray_typeinforangedType;

static PyStructSequence_Field typeinfo_fields[] = {
    {"char",      "The character used to represent the type"},
    {"num",       "The numeric id assigned to the type"},
    {"bits",      "The number of bits in the type"},
    {"alignment", "The alignment of the type in bytes"},
    {"type",      "The python type object this info is about"},
    {NULL, NULL,}
};

static PyStructSequence_Field typeinforanged_fields[] = {
    {"char",      "The character used to represent the type"},
    {"num",       "The numeric id assigned to the type"},
    {"bits",      "The number of bits in the type"},
    {"alignment", "The alignment of the type in bytes"},
    {"max",       "The maximum value of this type"},
    {"min",       "The minimum value of this type"},
    {"type",      "The python type object this info is about"},
    {NULL, NULL,}
};

static PyStructSequence_Desc typeinfo_desc = {
    "numpy.core.multiarray.typeinfo",         /* name          */
    "Information about a scalar numpy type",  /* doc           */
    typeinfo_fields,                          /* fields        */
    5,                                        /* n_in_sequence */
};

static PyStructSequence_Desc typeinforanged_desc = {
    "numpy.core.multiarray.typeinforanged",                /* name          */
    "Information about a scalar numpy type with a range",  /* doc           */
    typeinforanged_fields,                                 /* fields        */
    7,                                                     /* n_in_sequence */
};

PyObject *
PyArray_typeinfo(
    char typechar, int typenum, int nbits, int align,
    PyTypeObject *type_obj)
{
    PyObject *entry = PyStructSequence_New(&PyArray_typeinfoType);
    if (entry == NULL)
        return NULL;
#if defined(NPY_PY3K)
    PyStructSequence_SET_ITEM(entry, 0, Py_BuildValue("C", typechar));
#else
    PyStructSequence_SET_ITEM(entry, 0, Py_BuildValue("c", typechar));
#endif
    PyStructSequence_SET_ITEM(entry, 1, Py_BuildValue("i", typenum));
    PyStructSequence_SET_ITEM(entry, 2, Py_BuildValue("i", nbits));
    PyStructSequence_SET_ITEM(entry, 3, Py_BuildValue("i", align));
    PyStructSequence_SET_ITEM(entry, 4, Py_BuildValue("O", (PyObject *) type_obj));

    if (PyErr_Occurred()) {
        Py_DECREF(entry);
        return NULL;
    }

    return entry;
}

PyObject *
PyArray_typeinforanged(
    char typechar, int typenum, int nbits, int align,
    PyObject *max, PyObject *min, PyTypeObject *type_obj)
{
    PyObject *entry = PyStructSequence_New(&PyArray_typeinforangedType);
    if (entry == NULL)
        return NULL;
#if defined(NPY_PY3K)
    PyStructSequence_SET_ITEM(entry, 0, Py_BuildValue("C", typechar));
#else
    PyStructSequence_SET_ITEM(entry, 0, Py_BuildValue("c", typechar));
#endif
    PyStructSequence_SET_ITEM(entry, 1, Py_BuildValue("i", typenum));
    PyStructSequence_SET_ITEM(entry, 2, Py_BuildValue("i", nbits));
    PyStructSequence_SET_ITEM(entry, 3, Py_BuildValue("i", align));
    PyStructSequence_SET_ITEM(entry, 4, max);
    PyStructSequence_SET_ITEM(entry, 5, min);
    PyStructSequence_SET_ITEM(entry, 6, Py_BuildValue("O", (PyObject *) type_obj));

    if (PyErr_Occurred()) {
        Py_DECREF(entry);
        return NULL;
    }

    return entry;
}

void typeinfo_init_structsequences(void)
{
    PyStructSequence_InitType(
        &PyArray_typeinfoType, &typeinfo_desc);
    PyStructSequence_InitType(
        &PyArray_typeinforangedType, &typeinforanged_desc);
}
