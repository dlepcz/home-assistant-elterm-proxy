import asyncio
import socket
import json
import logging
from typing import Optional
from homeassistant.helpers.dispatcher import async_dispatcher_send
from .const import SIGNAL_UPDATE, CMD_TEMP_ENTITY, CMD_POWER_ENTITY

_LOGGER = logging.getLogger(__name__)

BUFFER_SIZE = 4096

class EltermProxy:
    def __init__(self, config, hass):
        self._hass = hass
        self._config = config
        self._server = None
        self._tasks = []
        self.token = "XXXXXX"
        self.dev_id = config.get("dev_id")
        self.dev_pin = config.get("dev_pin")
        self.last_temp = None
        self.last_power = None

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


class ProxyConnection(asyncio.Protocol):
    def __init__(self, proxy: EltermProxy):
        self.proxy = proxy
        self.transport = None
        self.remote_writer: Optional[asyncio.StreamWriter] = None
        self._forward_remote_task = None
        self._remote_connected = asyncio.Event()
        self._forward_loop_task = None
        self.response_buffer = ""

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
                    if 'Token' in json_data:
                        self.proxy.token = json_data['Token']
                except json.JSONDecodeError:
                    _LOGGER.debug("[S] Non-JSON data")
                self.transport.write(data)
        except Exception as e:
            _LOGGER.error("Remote error: %s", e)

    def data_received(self, data):
        decoded = data.decode(errors='ignore')
        self.response_buffer += decoded

        try:
            _LOGGER.debug("[C] %s", self.response_buffer.strip())
            parsed = json.loads(self.response_buffer)

            boiler_temp = self.proxy.get_command_from_state(CMD_TEMP_ENTITY, 6500)
            boiler_power = self.proxy.get_command_from_state(CMD_POWER_ENTITY, 67)

            if parsed.get("BoilerTempCmd") != boiler_temp:
                self.proxy.last_temp = boiler_temp
                self.send_command()

            if parsed.get("BuModulMax") != boiler_power:
                self.proxy.last_power = boiler_power
                self.send_command()

            async_dispatcher_send(self.proxy._hass, SIGNAL_UPDATE)
            self.response_buffer = ""

        except json.JSONDecodeError:
            _LOGGER.debug("[C] Waiting for full JSON chunk")

        if self._remote_connected.is_set():
            self.remote_writer.write(data)
        else:
            _LOGGER.warning("Skipping forward: remote not connected")

    def send_command(self):
        reply = {
            "FrameType": "DataToSen",
            "Token": self.proxy.token,
            "DevId": self.proxy.dev_id,
            "DevPin": self.proxy.dev_pin,
            "BoilerTempCmd": self.proxy.last_temp or 6500,
            "BoilerHist": "200",
            "CH1Mode": "Still_On",
            "BuModulMax": self.proxy.last_power or 2
        }
        msg = json.dumps(reply)
        _LOGGER.info("→ Sending to client: %s", msg)
        if self.transport:
            self.transport.write(msg.encode())
