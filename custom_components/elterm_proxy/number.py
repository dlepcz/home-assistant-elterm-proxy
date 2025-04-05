from homeassistant.components.number import NumberEntity
from .const import DOMAIN

CONTROL_PARAMS = {
    "SetBoilerTempCmd": {"min": 20, "max": 90, "step": 1, "unit": "°C", "scale": 100},
    "SetBuModulMax": {"min": 0, "max": 2, "step": 1, "unit": "mod", "scale": 1}
}

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    numbers = []
    for key in CONTROL_PARAMS:
        numbers.append(EltermNumber(hass, key))
        hass.data[DOMAIN]["entities"][key] = numbers[-1]
    async_add_entities(numbers)

class EltermNumber(NumberEntity):
    def __init__(self, hass, key):
        self._hass = hass
        self._key = key
        self._attr_name = f"Elterm {key}"
        self._attr_unique_id = f"elterm_{key.lower()}"
        self._attr_native_unit_of_measurement = CONTROL_PARAMS[key]["unit"]

    @property
    def native_value(self):
        raw = self._hass.data[DOMAIN]["values"].get(self._key)
        if raw is None:
            return None
        return int(raw) / CONTROL_PARAMS[self._key]["scale"]

    def set_native_value(self, value):
        scaled = int(value * CONTROL_PARAMS[self._key]["scale"])
        self._hass.services.call(DOMAIN, "set_elterm_parameters", {self._key: scaled})