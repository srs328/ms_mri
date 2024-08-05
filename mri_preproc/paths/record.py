from collections import defaultdict, namedtuple

from collections import defaultdict, namedtuple
from collections.abc import MutableSequence
from pathlib import Path
from typing import NamedTuple
import csv
from pprint import pp

Scan = namedtuple("Scan", ("subid", "date", "image", "label"))

# TODO try to make this a subclass of Sequence
#   https://stackoverflow.com/questions/46690012/subclassing-sequence-with-proper-type-hints-in-python


# Source: https://stackoverflow.com/questions/15418386/what-is-the-best-data-structure-for-storing-a-set-of-four-or-more-values
# make class method to return this given a csv, and another given a dict
class Record(MutableSequence):

    def __init__(self, recordname: str, fields: list, records=None):
        if records is None:
            records = []
        self.fields = fields
        defaults = [""]*len(fields)
        self.Data = namedtuple(recordname, self.fields, defaults=defaults)
        self._records = [self.Data(**record) for record in records]
        self.valid_fieldnames = set(self.fields)

        self.lookup_tables = {}

    def __getitem__(self, idx):
        return self._records[idx]

    def __setitem__(self, idx, val):
        self._records[idx] = self.Data(**val)

    def __delitem__(self, idx):
        del self._records[idx]

    def __len__(self):
        return len(self._records)

    def insert(self, idx, val):
        a = self._records[:idx]
        b = self._records[idx:]
        self._records = a + [self.Data(**val)] + b

    def retrieve(self, **kwargs):
        """Fetch a list of records with a field name with the value supplied
        as a keyword arg (or return None if there aren't any).
        """
        if len(kwargs) != 1:
            raise ValueError(
                "Exactly one fieldname keyword argument required for retrieve function "
                "(%s specified)" % ", ".join([repr(k) for k in kwargs.keys()])
            )
        field, value = kwargs.popitem()  # Keyword arg's name and value.
        if field not in self.valid_fieldnames:
            raise ValueError('keyword arg "%s" isn\'t a valid field name' % field)
        if field not in self.lookup_tables:  # Need to create a lookup table?
            lookup_table = self.lookup_tables[field] = defaultdict(list)
            for index, record in enumerate(self._records):
                field_value = getattr(record, field)
                lookup_table[field_value].append(index)
        # Return (possibly empty) sequence of matching records.
        return tuple(
            self._records[index] for index in self.lookup_tables[field].get(value, [])
        )


if __name__ == "__main__":
    empdb = Record("employees.csv", "Person")

    print(
        "retrieve(name='Ted Kingston'): {}".format(empdb.retrieve(name="Ted Kingston"))
    )
    print("retrieve(age='27'): {}".format(empdb.retrieve(age="27")))
    print("retrieve(weight='150'): {}".format(empdb.retrieve(weight="150")))
    try:
        print("retrieve(hight='5ft 6in'):".format(empdb.retrieve(hight="5ft 6in")))
    except ValueError as e:
        print("ValueError('{}') raised as expected".format(e))
    else:
        raise type("NoExceptionError", (Exception,), {})(
            "No exception raised from \"retrieve(hight='5ft')\" call."
        )
