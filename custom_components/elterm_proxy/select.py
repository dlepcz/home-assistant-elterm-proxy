import logging
from . import EltermProxy, EltermEntity
from .const import DOMAIN
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
    async_add_entities(
        [
            EltermBoilerPowerSelect(
                proxy,
                unique_id=f"{proxy.name}_setBoilerTempCmd",
                device_name=f"{proxy.name} Boiler power",
                current_option="67%",
                options=[
                    "33%",
                    "67%",
                    "100%",
                ],
                translation_key=f"{proxy.name}_setBoilerTempCmd"
            ),
        ]
    )


class EltermBoilerPowerSelect(EltermEntity, SelectEntity):

    #_attr_has_entity_name = True
    #_attr_name = None
    #_attr_should_poll = False

    def __init__(
        self,
        proxy: EltermProxy,
        unique_id: str,
        device_name: str,
        current_option: str | None,
        options: list[str],
        translation_key: str,
    ) -> None:
        super().__init__(proxy)
        self._attr_unique_id = unique_id
        self._attr_has_entity_name = True
        self._attr_current_option = current_option
        self._attr_options = options
        self._attr_translation_key = translation_key
        
    @callback
    def _handle_coordinator_update(self) -> None:
        super()._handle_coordinator_update()

    async def async_select_option(self, option: str) -> None:
        if option == "33%":
            self.proxy.boiler_power = 0
        elif option == "100%":
            self.proxy.boiler_power = 2
        else:
            self.proxy.boiler_power = 1
        self._attr_current_option = option
        self.async_write_ha_state()
