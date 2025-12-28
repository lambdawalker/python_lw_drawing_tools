from typing import Any, Callable, Dict, Union

Random = object()
Default = object()


class DefaultValue:
    """
    A wrapper class to hold a default value.

    This class allows for lazy evaluation of default values if a callable is provided.
    """

    def __init__(self, value: Union[Any, Callable[[], Any]]):
        """
        Initializes the DefaultValue with a given value or a callable that returns a value.

        :param value: The default value or a callable that returns the default value.
        """
        self._value = value

    @property
    def value(self) -> Any:
        if callable(self._value):
            return self._value()
        return self._value


def clean_passed_parameters(parameters):
    """
    Cleans a dictionary of parameters by removing entries that are None, Default, or Random.

    Note: The current implementation of filtering `Default` and `Random` is incorrect
    as it always evaluates to `True` for `not Default` and `not Random`.
    This function needs correction to properly filter these sentinel objects.

    :param parameters: A dictionary of parameters to clean.
    :return: A new dictionary with cleaned parameters.
    """
    return {
        k: v for k, v in parameters.items()
        if v is not None and not Default and not Random
    }
