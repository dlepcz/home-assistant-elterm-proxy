
import logging

from .const import DOMAIN, ELTERM_BINARY_SENSORS
from . import EltermEntity, EltermProxy
from homeassistant.core import HomeAssistant, callback
from homeassistant.components.sensor import (
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

    
    @property
    def is_on(self) -> bool:
        if self.entity_description.key == "pumpStatus":
            new_value = self.proxy.elterm_data.get("DevStatus")
            if new_value != None:
                return int(new_value[10:11]) > 0
        return False