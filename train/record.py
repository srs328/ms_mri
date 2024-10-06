from collections import defaultdict, namedtuple

from collections import defaultdict, namedtuple
from collections.abc import MutableSequence, Sequence


# based on: https://stackoverflow.com/questions/15418386/what-is-the-best-data-structure-for-storing-a-set-of-four-or-more-values
class Record(MutableSequence):

    def __init__(self, recordname: str, fields: list, records=None):
        if records is None:
            records = []
        self.fields = fields
        defaults = [""] * len(fields)
        self.Data = namedtuple(recordname, self.fields, defaults=defaults)
        self._records = [self.Data(**record) for record in records]
        self.valid_fieldnames = set(self.fields)

        self.lookup_tables: dict = {}

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
        if isinstance(val, self.Data):
            self._records = a + [val] + b
        else:
            self._records = a + [self.Data(**val)] + b

    def retrieve(self, get_index=False, **kwargs):
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
        if get_index:
            return tuple(self.lookup_tables[field].get(value, []))
        else:
            return tuple(
                self._records[index]
                for index in self.lookup_tables[field].get(value, [])
            )
