import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from .const import DOMAIN, SIGNAL_UPDATE

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    proxy = hass.data[DOMAIN][config_entry.entry_id]
    sensors = [
        EltermProxySensor(proxy, "elterm_boiler_temp", "Elterm Boiler Temperature", "°C"),
        EltermProxySensor(proxy, "elterm_boiler_current_temp", "Elterm Boiler Current Temperature", "°C"),
        EltermProxySensor(proxy, "elterm_boiler_power", "Elterm Boiler Power", "%"),
        EltermProxySensor(proxy, "elterm_boiler_token", "Elterm Boiler Token", None)
    ]
    async_add_entities(sensors)

    async def handle_update():
        for sensor in sensors:
            sensor.update_state()
            sensor.async_schedule_update_ha_state()

    async_dispatcher_connect(hass, SIGNAL_UPDATE, handle_update)


class EltermProxySensor(SensorEntity):
    def __init__(self, proxy, key, name, unit):
        self._proxy = proxy
        self._key = key
        self._name = name
        self._unit = unit
        self._state = None

    @property
    def name(self):
        return self._name

    @property
    def native_value(self):
        return self._state

    @property
    def native_unit_of_measurement(self):
        return self._unit

    @property
    def unique_id(self):
        return f"{DOMAIN}_{self._key}"

    def update_state(self):
        if self._key == "elterm_boiler_temp":
            self._state = self._proxy.last_temp / 100
        elif self._key == "elterm_boiler_power":
            if self._proxy.last_power == 1:
                self._state = 33
            elif self._proxy.last_power == 2:
                self._state = 67
            else:
                self._state = 100         
        elif self._key == "elterm_boiler_token":
            self._state = self._proxy.token
        elif self._key == "elterm_boiler_current_temp":
            self._state = self._proxy.BoilerTempAct / 100