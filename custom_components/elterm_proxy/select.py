import logging
from .const import DOMAIN
from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    async_add_entities(
        [
            EltermBoilerPowerSelect(
                unique_id="elterm_setBoilerTempCmd",
                device_name="Power",
                current_option="67%",
                options=[
                    "33%",
                    "67%",
                    "100%",
                ]
            ),
        ]
    )


class EltermBoilerPowerSelect(SelectEntity):
    """Representation of a demo select entity."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_should_poll = False

    def __init__(
        self,
        unique_id: str,
        device_name: str,
        current_option: str | None,
        options: list[str],
        translation_key: str | None,
    ) -> None:
        self._attr_unique_id = unique_id
        self._attr_current_option = current_option
        self._attr_options = options
        self._attr_translation_key = translation_key
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, unique_id)},
            name=device_name,
        )

    async def async_select_option(self, option: str) -> None:
        self._attr_current_option = option
        self.async_write_ha_state()
