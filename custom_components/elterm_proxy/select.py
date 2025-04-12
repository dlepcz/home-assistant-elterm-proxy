import logging
from . import EltermProxy, EltermEntity
from .const import (
    DOMAIN, 
    ELTERM_CONTROL_SELECT,
    EltermSelectDescription,
)
from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    proxy = hass.data[DOMAIN][config_entry.entry_id]
    entities = []

    for entity in ELTERM_CONTROL_SELECT:
        entities.append(EltermBoilerPowerSelect(proxy, entity))

    async_add_entities(entities)

def get_key(my_dict, search):
    for key, value in my_dict.items():
        if value == search:
            return key
    return None

def get_value(my_dict, search):
    for key, value in my_dict.items():
        if key == search:
            return value
    return None

class EltermBoilerPowerSelect(EltermEntity, SelectEntity):

    def __init__(
        self,
        proxy: EltermProxy,
        description: EltermSelectDescription,
    ) -> None:
        super().__init__(proxy)
        self._attr_has_entity_name = True
        self.entity_description = description
        self._attr_unique_id = f"{self.proxy.name}_{description.key}"
        self._option_dict = description.options_dict
        self._attr_options = list(description.options_dict.values())
        self._attr_current_option = "67%"
    
    @property
    def current_option(self) -> str:
        return get_value(self._option_dict, self.proxy.boiler_power)

    @callback
    def _handle_coordinator_update(self) -> None:
        super()._handle_coordinator_update()

    async def async_select_option(self, option: str) -> None:
        new_mode = get_key(self._option_dict, option)
        self.proxy.boiler_power = new_mode
        _LOGGER.debug(f"Update boiler power to {self.proxy.boiler_power}")
        self.async_write_ha_state()