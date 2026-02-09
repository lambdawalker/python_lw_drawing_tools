class Record:
    def __init__(self, data: dict):
        # We store the data in a private attribute
        self._data = data

    def __getattr__(self, name):
        if name in self._data:
            return self._data[name]
        raise AttributeError(f"Record has no field '{name}'")

    def __getitem__(self, key):
        return self._data[key]

    def __repr__(self):
        keys = ", ".join(self._data.keys())
        return f"Record({keys})"

    # Allow iteration over keys like a dict
    def keys(self):
        return self._data.keys()
