import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from .const import DOMAIN, ELTERM_SENSORS
from . import EltermEntity, EltermProxy
from homeassistant.components.sensor import (
    SensorEntity,
    SensorEntityDescription,
    SensorDeviceClass
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

        if self.entity_description.device_class == SensorDeviceClass.TEMPERATURE:
            self._attr_native_value = int(new_value) / 100
        elif self.entity_description.key == "BuModulMax":
            match new_value:
                case "0":
                    self._attr_native_value = "33%"
                case "1":
                    self._attr_native_value = "67%"
                case "2":
                    self._attr_native_value = "100%"
                case _:
                    self._attr_native_value = None
        else:    
            self._attr_native_value = new_value

        super()._handle_coordinator_update()
