"""Configuration class for the load button configuration property."""

from __future__ import annotations

from typing import Union

from ..address import Address
from .derived_property import DerivedProperty
from .extended_property import ExtendedProperty


class LoadButtonProperty(DerivedProperty):
    """Derived property for the load button property."""

    def __init__(
        self,
        address: Address,
        name: str,
        load_button_prop: ExtendedProperty,
        allowed_values: list,
    ) -> None:
        """Init the LoadButtonProperty class."""
        super().__init__(address, name, list, False, False)
        self._load_button_prop = load_button_prop
        self._allowed_values = allowed_values

    @property
    def value(self) -> Union[int, None]:
        """Return the value of the load button from the underlying property."""
        return self._load_button_prop.value

    @property
    def new_value(self) -> Union[int, None]:
        """Return the modified value of the property."""
        return self._load_button_prop.new_value

    @new_value.setter
    def new_value(self, value) -> None:
        """Modify the value of the property.

        Set value to one of the device buttons.

        Set `new_value` to `None` to retain the current load button value.
        """

        if value is not None and value not in self._allowed_values:
            raise ValueError(f"Value must be None or one of {self._allowed_values}")
        self._load_button_prop.new_value = value

    @property
    def is_dirty(self) -> bool:
        """Return if the underlying property values have changed."""
        return self._load_button_prop.is_dirty

    @property
    def is_loaded(self) -> bool:
        """Return if the underlying property values are loaded.."""
        return self._load_button_prop.is_loaded
