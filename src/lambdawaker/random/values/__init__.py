Random = object()
Default = object()


class DefaultValue:
    def __init__(self, value):
        self._value = value

    @property
    def value(self):
        if callable(self._value):
            return self._value()
        return self._value


def clean_passed_parameters(parameters):
    return {
        k: v for k, v in parameters.items()
        if v is not None and not Default and not Random
    }
