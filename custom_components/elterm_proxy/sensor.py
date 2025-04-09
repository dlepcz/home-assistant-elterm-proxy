import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from .const import DOMAIN, ELTERM_SENSORS
from . import EltermEntity, EltermProxy
from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.core import HomeAssistant, callback

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, config_entry, async_add_entities):
    proxy = hass.data[DOMAIN][config_entry.entry_id]

    entities = []

    for entity in ELTERM_SENSORS:
        entities.append(EltermProxySensor(proxy, entity))

    async_add_entities(entities)


class EltermProxySensor(EltermEntity, SensorEntity):
    def __init__(
        self, proxy: EltermProxy, description: SensorEntityDescription
    ) -> None:
        super().__init__(proxy)
        self.entity_description = description
        self._attr_has_entity_name = True
        self._attr_unique_id = f"{self.proxy.name}_{description.key}"

    @callback
    def _handle_coordinator_update(self) -> None:
        new_value = self.proxy.elterm_data.get(self.entity_description.key)
        _LOGGER.debug("Update sensor %s to %s", self.entity_description.key, new_value)
        self._attr_native_value = new_value

        super()._handle_coordinator_update()
