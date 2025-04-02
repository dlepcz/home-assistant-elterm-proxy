import asyncio
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN
from .proxy import EltermProxy

_LOGGER = logging.getLogger(__name__)

async def async_setup(hass: HomeAssistant, config: dict):
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    _LOGGER.info("Setting up Elterm Proxy integration")

    proxy = EltermProxy(entry.data, hass)
    await proxy.start()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = proxy

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    proxy: EltermProxy = hass.data[DOMAIN].pop(entry.entry_id)
    await proxy.stop()

    return await hass.config_entries.async_forward_entry_unload(entry, "sensor")