import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from .const import DOMAIN, ELTERM_SENSORS
from . import EltermEntity, EltermProxy
from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
)

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
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
