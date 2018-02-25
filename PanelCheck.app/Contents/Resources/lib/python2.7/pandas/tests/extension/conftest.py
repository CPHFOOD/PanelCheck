import operator

import pytest


@pytest.fixture
def dtype():
    """A fixture providing the ExtensionDtype to validate."""
    raise NotImplementedError


@pytest.fixture
def data():
    """Length-100 array for this type."""
    raise NotImplementedError


@pytest.fixture
def data_missing():
    """Length-2 array with [NA, Valid]"""
    raise NotImplementedError


@pytest.fixture(params=['data', 'data_missing'])
def all_data(request, data, data_missing):
    """Parametrized fixture giving 'data' and 'data_missing'"""
    if request.param == 'data':
        return data
    elif request.param == 'data_missing':
        return data_missing


@pytest.fixture
def na_cmp():
    """Binary operator for comparing NA values.

    Should return a function of two arguments that returns
    True if both arguments are (scalar) NA for your type.

    By default, uses ``operator.or``
    """
    return operator.is_


@pytest.fixture
def na_value():
    """The scalar missing value for this type. Default 'None'"""
    return None
