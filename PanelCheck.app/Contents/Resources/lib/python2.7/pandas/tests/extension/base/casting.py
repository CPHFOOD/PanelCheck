import pandas as pd
from pandas.core.internals import ObjectBlock

from .base import BaseExtensionTests


class BaseCastingTests(BaseExtensionTests):
    """Casting to and from ExtensionDtypes"""

    def test_astype_object_series(self, all_data):
        ser = pd.Series({"A": all_data})
        result = ser.astype(object)
        assert isinstance(result._data.blocks[0], ObjectBlock)
