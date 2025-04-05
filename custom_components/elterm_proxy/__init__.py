import asyncio
import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
import voluptuous as vol
from .const import DOMAIN
from .proxy import EltermProxy

_LOGGER = logging.getLogger(__name__)

CONF_TEMP = "SetBoilerTempCmd"
CONF_MODUL = "SetBuModulMax"

async def async_setup(hass: HomeAssistant, config: dict):
    hass.data[DOMAIN] = {}
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    _LOGGER.info("Setting up Elterm Proxy integration")

    async def handle_command(call):
        _LOGGER.debug("handle_command")

    proxy = EltermProxy(entry.data, hass)
    await proxy.start()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = proxy

    await hass.config_entries.async_forward_entry_setups(entry, ["sensor"])

    hass.services.async_register(DOMAIN, "set_elterm_parameters", handle_command,vol.Schema({vol.Optional(CONF_TEMP): vol.Coerce(int),vol.Optional(CONF_MODUL): vol.Coerce(int)}))
    #hass.async_create_task(hass.helpers.discovery.async_load_platform("sensor", DOMAIN, {}, entry))
    #hass.async_create_task(hass.helpers.discovery.async_load_platform("number", DOMAIN, {}, hass.helpers.discovery.async_load_platform("sensor", DOMAIN, {}, entry)))

    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    proxy: EltermProxy = hass.data[DOMAIN].pop(entry.entry_id)
    await proxy.stop()

    return await hass.config_entries.async_forward_entry_unload(entry, "sensor")