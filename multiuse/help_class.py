"""
Helper classes for routine procedures.
Int8 can store integers from -128 to 127
Int16 can store integers from -32768 to 32767
Int32 can store integers from -2,147,483,648 to 2,147,483,648
Int64

uint8: Unsigned integer (0 to 255)
uint16: Unsigned integer (0 to 65535)
uint32: Unsigned integer (0 to 4294967295)

"""
# %% codecell
import pandas as pd
import numpy as np
from dotenv import load_dotenv

import os
from pathlib import Path
from datetime import timedelta, date
import datetime
import pytz

# %% codecell
###############################################################################

class baseDir():
    """Get the current base directory and adjust accordingly."""
    load_dotenv()
    env = os.environ.get("env")

    def __init__(self):
        if self.env == 'production':
            self.path = f"{Path(os.getcwd())}/data"
        else:
            self.path = f"{Path(os.getcwd()).parents[0]}/data"


class scriptDir():
    """Get the current base directory and adjust accordingly."""
    load_dotenv()
    env = os.environ.get("env")

    def __init__(self):
        if self.env == 'production':
            self.path = f"{Path(os.getcwd())}/scripts/dev/data_collect"
        else:
            self.path = f"{Path(os.getcwd()).parents[0]}/dev/data_collect"

# %% codecell
###############################################################################
class getDate():
    """Get the right query date."""

    @staticmethod
    def which_fname_date():
        """Figure out which date to use for file names."""
        nyc_datetime = datetime.datetime.now(pytz.timezone('US/Eastern'))
        nyc_hm = nyc_datetime.hour + (nyc_datetime.minute/60)
        cutoff_hm = 9.55  # Past 9:30 AM

        date_today = date.today().weekday()
        weekdays = (0, 1, 2, 3, 4)

        if (nyc_hm < cutoff_hm) and (date_today in weekdays):
            da_min = 1
        else:
            da_min = 0

        if date_today == 0:
            days = 3 + da_min
        elif date_today in weekdays:  # Get previous day data
            days = 1 + da_min
        elif date_today == 5:  # Saturday get thursday data
            days = 2
        elif date_today == 6:
            days = 3

        fname_date = (date.today() - timedelta(days=days))

        return fname_date

    @staticmethod
    def query(site):
        """Call which_fname_date but shorter."""
        query_date = getDate.which_fname_date()
        if site in ('cboe', 'occ'):
            query_date = query_date + timedelta(days=1)
        elif site in ('last_syms'):
            pass
        return query_date

# %% codecell
###############################################################################

class dataTypes():
    """Helper class for implementing data type conversions."""

    def __init__(self, df):
        self.dtypes = df.dtypes
        self.df = df.copy(deep=True)
        self._cols_to_cat(self)
        self.pos_or_neg_ints(self)
        self.pos_or_neg_floats(self)
        print('Modified dataframe accessible with xxx.df')

    @classmethod
    def _cols_to_cat(cls, self):
        """Convert object columns to categorical."""
        cols_to_cat = self.dtypes[self.dtypes == 'object'].index.to_list()
        self.df[cols_to_cat] = self.df[cols_to_cat].astype('category')

    @classmethod
    def pos_or_neg_ints(cls, self):
        """Convert integers to correct data type."""
        cols_int64 = self.dtypes[self.dtypes == 'int64'].index.to_list()
        int8_val = 127
        int16_val = 32767
        int32_val = 2147483648

        for col in cols_int64:
            min = self.df[col].min()
            max = self.df[col].max()
            if min >= 0:
                if max < 255:
                    self.df[col] = self.df[col].astype(np.uint8)
                elif max < 65535:
                    self.df[col] = self.df[col].astype(np.uint16)
                elif max < 4294967295:
                    self.df[col] = self.df[col].astype(np.uint32)
            else:
                if max < int8_val and min > -int8_val:
                    self.df[col] = self.df[col].astype(np.int8)
                elif max < int16_val and min > -int16_val:
                    self.df[col] = self.df[col].astype(np.int16)
                elif max < int32_val and min > -int32_val:
                    self.df[col] = self.df[col].astype(np.int32)

    @classmethod
    def pos_or_neg_floats(cls, self):
        """Convert floats to correct data type."""
        cols_float64 = self.dtypes[self.dtypes == 'float64'].index.to_list()
        self.df[cols_float64] = self.df[cols_float64].astype(np.float16)



# %% codecell
###############################################################################