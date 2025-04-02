import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, DEFAULT_LISTEN_PORT, DEFAULT_FORWARD_HOST, DEFAULT_FORWARD_PORT, DEFAULT_DEV_ID, DEFAULT_DEV_PIN

class EltermProxyConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Elterm Proxy", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("listen_port", default=DEFAULT_LISTEN_PORT): int,
                vol.Required("forward_host", default=DEFAULT_FORWARD_HOST): str,
                vol.Required("forward_port", default=DEFAULT_FORWARD_PORT): int,
                vol.Required("dev_id", default=DEFAULT_DEV_ID): str,
                vol.Required("dev_pin", default=DEFAULT_DEV_PIN): str
            })
        )
