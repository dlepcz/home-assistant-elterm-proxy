
import logging

from .const import DOMAIN, ELTERM_BINARY_SENSORS
from . import EltermEntity, EltermProxy
from homeassistant.core import HomeAssistant, callback
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    proxy = hass.data[DOMAIN][config_entry.entry_id]

    entities = []

    for entity in ELTERM_BINARY_SENSORS:
        entities.append(EltermProxyBinarySensor(proxy, entity))

    async_add_entities(entities)

class EltermProxyBinarySensor(EltermEntity, BinarySensorEntity):
    def __init__(
        self, proxy: EltermProxy, description: BinarySensorEntityDescription
    ) -> None:
        super().__init__(proxy)
        self.entity_description = description
        self._attr_has_entity_name = True
        self._attr_unique_id = f"{self.proxy.name}_{description.key}"

    @callback
    def _handle_coordinator_update(self) -> None:
        if self.entity_description.key == "pumpIsRunning":
            new_value = self.proxy.elterm_data.get("DevStatus")
            if new_value != None:
                self._attr_is_on = int(new_value[10:11]) > 0
        else:
            self._attr_is_on = False