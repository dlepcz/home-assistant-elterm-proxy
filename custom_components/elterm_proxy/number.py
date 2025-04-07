from __future__ import annotations
from . import EltermProxy, EltermEntity
from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    proxy = hass.data[DOMAIN][config_entry.entry_id]
    async_add_entities(
        [
            EltermBoilerNumber(
                proxy,
                f"{proxy.name}_setBoilerTemp",
                f"{proxy.name} Temperature",
                40,
                None,
                False,
                device_class=NumberDeviceClass.TEMPERATURE,
                native_min_value=20,
                native_max_value=70,
                native_step=1,
                mode=NumberMode.BOX,
                unit_of_measurement=UnitOfTemperature.CELSIUS,
            ),
        ]
    )


class EltermBoilerNumber(EltermEntity, NumberEntity):

    _attr_has_entity_name = True
    _attr_name = None
    _attr_should_poll = False

    def __init__(
        self,
        proxy: EltermProxy,
        unique_id: str,
        device_name: str,
        state: float,
        translation_key: str | None,
        assumed_state: bool,
        *,
        device_class: NumberDeviceClass | None = None,
        mode: NumberMode = NumberMode.AUTO,
        native_min_value: float | None = None,
        native_max_value: float | None = None,
        native_step: float | None = None,
        unit_of_measurement: str | None = None,
    ) -> None:
        self._attr_assumed_state = assumed_state
        self._attr_device_class = device_class
        self._attr_translation_key = translation_key
        self._attr_mode = mode
        self._attr_native_unit_of_measurement = unit_of_measurement
        self._attr_native_value = state
        self._attr_unique_id = unique_id

        if native_min_value is not None:
            self._attr_native_min_value = native_min_value
        if native_max_value is not None:
            self._attr_native_max_value = native_max_value
        if native_step is not None:
            self._attr_native_step = native_step

    async def async_set_native_value(self, value: float) -> None:
        self._attr_native_value = value
        self.async_write_ha_state()
