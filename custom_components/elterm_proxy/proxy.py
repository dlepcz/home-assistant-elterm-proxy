import asyncio
import socket
import json
import logging
import re
from datetime import timedelta
from typing import Optional
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.const import CONF_NAME
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.core import HomeAssistant
from .const import SIGNAL_UPDATE, UPDATE_INTERVAL, ELTERM_DATA

_LOGGER = logging.getLogger(__name__)

BUFFER_SIZE = 4096

class EltermProxy(DataUpdateCoordinator):
    def __init__(
        self, 
        config, 
        hass: HomeAssistant,
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name=config.get(CONF_NAME),
            update_interval=timedelta(seconds=UPDATE_INTERVAL),
        )
        self._hass = hass
        self._config = config
        self._server = None
        self._tasks = []
        self.boiler_temp = "6500"
        self.boiler_power = "1"
        self.name = config.get(CONF_NAME)
        self.dev_id = config.get("dev_id")
        self.dev_pin = config.get("dev_pin")
        self.elterm_data ={}

    async def start(self):
        loop = asyncio.get_running_loop()
        server = await loop.create_server(
            lambda: ProxyConnection(self),
            host="0.0.0.0",
            port=self._config.get("listen_port")
        )
        self._server = server
        _LOGGER.info("Listening on 0.0.0.0:%d", self._config.get("listen_port"))

    async def stop(self):
        if self._server:
            self._server.close()
            await self._server.wait_closed()

    def get_command_from_state(self, entity_id: str, default: int) -> int:
        state = self._hass.states.get(entity_id)
        try:
            return int(state.state) if state and state.state != "unknown" else default
        except (ValueError, TypeError):
            return default
        
    async def _async_update_data(self) -> dict:
        try:
            return self.elterm_data
        except Exception as err:
            raise UpdateFailed(f"Error get data: {err}")


class ProxyConnection(asyncio.Protocol):
    def __init__(self, proxy: EltermProxy):
        self.proxy = proxy
        self.transport = None
        self.remote_writer: Optional[asyncio.StreamWriter] = None
        self._forward_remote_task = None
        self._remote_connected = asyncio.Event()
        self._forward_loop_task = None
        self.response_buffer = ""
        self.server_token = None

    def connection_made(self, transport):
        self.transport = transport
        self._forward_loop_task = asyncio.create_task(self.start_forward_loop())

    def connection_lost(self, exc):
        _LOGGER.info("Client disconnected")
        if self._forward_remote_task:
            self._forward_remote_task.cancel()
        if self.remote_writer:
            try:
                self.remote_writer.close()
                asyncio.create_task(self.remote_writer.wait_closed())
            except Exception:
                pass
        if self._forward_loop_task:
            self._forward_loop_task.cancel()

    async def start_forward_loop(self):
        while True:
            try:
                reader, writer = await asyncio.open_connection(
                    self.proxy._config.get("forward_host"),
                    self.proxy._config.get("forward_port")
                )
                self.remote_writer = writer
                self._remote_connected.set()
                _LOGGER.info("Connected to forward host")
                self._forward_remote_task = asyncio.create_task(self.forward_remote(reader))
                await self._forward_remote_task
            except asyncio.CancelledError:
                break
            except Exception as e:
                _LOGGER.warning("Forward connection failed or lost: %s", e)
                self._remote_connected.clear()
                await asyncio.sleep(10)

    async def forward_remote(self, reader):
        try:
            while True:
                data = await reader.read(BUFFER_SIZE)
                if not data:
                    break
                decoded = data.decode(errors='ignore')
                _LOGGER.debug("[S] %s", decoded.strip())
                try:
                    json_data = json.loads(decoded)
                    if 'Token' in json_data and self.server_token != json_data['Token']:
                        self.server_token = json_data['Token']
                        _LOGGER.debug("New server token = %s", self.server_token)
                        self.proxy.elterm_data["serverToken"] = self.server_token

                except json.JSONDecodeError:
                    _LOGGER.debug("[S] Non-JSON data")
                self.transport.write(data)
        except Exception as e:
            _LOGGER.error("Remote error: %s", e)

    def data_received(self, data):
        decoded = data.decode(errors='ignore')
        self.response_buffer += decoded

        match = re.search(r'\{.*?\}', self.response_buffer)
        if match:
            try:
                _LOGGER.debug("-------------------------")
                _LOGGER.debug("[C] %s", self.response_buffer.strip())
                _LOGGER.debug("-------------------------")
                self.response_buffer = ""
                parsed = json.loads(match.group(0))
          
                for k, v in ELTERM_DATA.items():
                    if k[0].isupper():
                        self.proxy.elterm_data[k] = parsed.get(k)

                if self.proxy.elterm_data["BoilerTempCmd"] != self.proxy.boiler_temp or self.proxy.elterm_data["BuModulMax"] != self.proxy.boiler_power:
                    self.send_command()
                    
            except json.JSONDecodeError:
                _LOGGER.debug("[C] Waiting for full JSON chunk")
            finally:
                self.response_buffer = ""

        if self._remote_connected.is_set():
            self.remote_writer.write(data)
        else:
            _LOGGER.warning("Skipping forward: remote not connected")

    def send_command(self):
        if not all([self.server_token, self.proxy.dev_id, self.proxy.dev_pin]):
            _LOGGER.debug("ServerToken=%s;dev_id=%s;;dev_pin=%s", self.server_token,self.proxy.dev_id, self.proxy.dev_pin);
            _LOGGER.warning("Empty ServerToken/DevId/DevPin")
            return
        reply = {
            "FrameType": "DataToSen",
            "Token": self.server_token,
            "DevId": self.proxy.dev_id,
            "DevPin": self.proxy.dev_pin,
            "BoilerTempCmd": self.proxy.boiler_temp,
            "BoilerHist": self.proxy.elterm_data["BoilerHist"],
            "CH1Mode": "Still_On",
            "BuModulMax": self.proxy.boiler_power
        }
        msg = json.dumps(reply)
        _LOGGER.debug("→ Sending to client: %s", msg)
        if self.transport:
            self.transport.write(msg.encode())

    
