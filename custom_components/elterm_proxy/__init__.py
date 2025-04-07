import asyncio
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)
from homeassistant.const import CONF_NAME
import voluptuous as vol
from .const import DOMAIN, ATTR_MANUFACTURER
from .proxy import EltermProxy

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["number", "select", "sensor"]

async def async_setup(hass: HomeAssistant, config: dict):
    hass.data[DOMAIN] = {}
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    _LOGGER.info("Setting up Elterm Proxy integration")
    
    proxy = EltermProxy(entry.data, hass)
    await proxy.start()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = proxy

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    proxy: EltermProxy = hass.data[DOMAIN].pop(entry.entry_id)
    await proxy.stop()

    return await hass.config_entries.async_forward_entry_unload(entry, PLATFORMS)

class EltermEntity(CoordinatorEntity):

    def __init__(self, proxy: EltermProxy) -> None:
       
        super().__init__(proxy)
        self.proxy = proxy
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, proxy.name)},
            manufacturer=ATTR_MANUFACTURER,
            name=proxy.name,
        )