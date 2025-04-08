from __future__ import annotations
from . import EltermProxy, EltermEntity
from homeassistant.components.number import NumberDeviceClass, NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.components.number import NumberEntityDescription

from .const import DOMAIN, ELTERM_CONTROL_TEMPERATURE


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    proxy = hass.data[DOMAIN][config_entry.entry_id]
    entities = []

    for entity in ELTERM_CONTROL_TEMPERATURE:
        entities.append(EltermBoilerNumber(proxy, entity))

    async_add_entities(entities)


class EltermBoilerNumber(EltermEntity, NumberEntity):
    def __init__(
        self, proxy: EltermProxy, description: NumberEntityDescription
    ) -> None:
        """Init."""
        super().__init__(proxy)
        self.entity_description = description
        self._attr_has_entity_name = True
        self._attr_unique_id = f"{self.proxy.name}_{description.key}"
        self._register = description.register
        self._attr_native_min_value = description.attrs["min"]
        self._attr_native_max_value = description.attrs["max"]
        self._attr_native_value = description.attrs["default"]

    @property
    def current_option(self) -> str:
        return int(self.proxy.boiler_temp) / 100
    
    async def async_set_native_value(self, value: float) -> None:
        self.proxy.boiler_temp = str(value * 100)
        self._attr_native_value = value
        self.async_write_ha_state()
