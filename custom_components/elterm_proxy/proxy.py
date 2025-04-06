import asyncio
import socket
import json
import logging
import re
from typing import Optional
from homeassistant.helpers.dispatcher import async_dispatcher_send
from homeassistant.const import CONF_NAME
from .const import SIGNAL_UPDATE, CMD_TEMP_ENTITY, CMD_POWER_ENTITY

_LOGGER = logging.getLogger(__name__)

BUFFER_SIZE = 4096

class EltermProxy:
    def __init__(self, config, hass):
        self._hass = hass
        self._config = config
        self._server = None
        self._tasks = []
        self.name = config.get(CONF_NAME)
        self.serverToken = "XXXXXX"
        self.dev_id = config.get("dev_id")
        self.dev_pin = config.get("dev_pin")
        self.devId = None
        self.devPin = None
        self.token = None
        self.frameType = None
        self.timeStamp = None
        self.devStatus = None
        self.alarms = None
        self.boilerTempAct = None
        self.boilerTempCmd = None
        self.boilerHist = None
        self.dHWTempAct = None
        self.dHWTempCmd = None
        self.dHWOverH = None
        self.dHWHist = None
        self.dHWMode = None
        self.cH1RoomTempAct = None
        self.cH1RoomTempCom = None
        self.cH1RoomTempCmd = None
        self.cH1RoomHist = None
        self.cH1Mode = None
        self.weaTempAct = None
        self.weaCorr = None
        self.upTime = None
        self.buModulMax = None
        self.p001 = None
        self.p002 = None
        self.p003 = None
        self.p004 = None
        self.p005 = None
        self.p006 = None
        self.p007 = None
        self.p008 = None
        self.p009 = None
        self.p011 = None
        self.p012 = None
        self.p013 = None
        self.p014 = None
        self.p015 = None
        self.p016 = None
        self.p017 = None
        self.p018 = None
        self.p019 = None
        self.p021 = None
        self.p022 = None
        self.p023 = None
        self.p024 = None
        self.p025 = None
        self.p026 = None
        self.p027 = None
        self.p028 = None
        self.p029 = None
        self.p030 = None
        self.p031 = None
        self.p032 = None
        self.p033 = None
        self.p034 = None
        self.p035 = None
        self.p036 = None
        self.devType = None

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
                        if self.update(serverToken = json_data['Token']):
                             async_dispatcher_send(self.proxy._hass, SIGNAL_UPDATE)
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
          
                boiler_temp = str(self.proxy.get_command_from_state(CMD_TEMP_ENTITY, 65) * 100)
                boiler_power = str(self.proxy.get_command_from_state(CMD_POWER_ENTITY, 1))

                if self.update(devId=parsed.get("DevId"),
                    devPin = parsed.get("DevPin"),
                    token = parsed.get("Token"),
                    frameType = parsed.get("FrameType"),
                    timeStamp = parsed.get("TimeStamp"),
                    devStatus = parsed.get("DevStatus"),
                    alarms = parsed.get("Alarms"),
                    boilerTempAct = parsed.get("BoilerTempAct"),
                    boilerTempCmd = parsed.get("BoilerTempCmd"),
                    boilerHist = parsed.get("BoilerHist"),
                    dHWTempAct = parsed.get("DHWTempAct"),
                    dHWTempCmd = parsed.get("DHWTempCmd"),
                    dHWOverH = parsed.get("DHWOverH"),
                    dHWHist = parsed.get("DHWHist"),
                    dHWMode = parsed.get("DHWMode"),
                    cH1RoomTempAct = parsed.get("CH1RoomTempAct"),
                    cH1RoomTempCom = parsed.get("CH1RoomTempCom"),
                    cH1RoomTempCmd = parsed.get("CH1RoomTempCmd"),
                    cH1RoomHist = parsed.get("CH1RoomHist"),
                    cH1Mode = parsed.get("CH1Mode"),
                    weaTempAct = parsed.get("WeaTempAct"),
                    weaCorr = parsed.get("WeaCorr"),
                    upTime = parsed.get("UpTime"),
                    buModulMax = parsed.get("BuModulMax"),
                    p001 = parsed.get("P001"),
                    p002 = parsed.get("P002"),
                    p003 = parsed.get("P003"),
                    p004 = parsed.get("P004"),
                    p005 = parsed.get("P005"),
                    p006 = parsed.get("P006"),
                    p007 = parsed.get("P007"),
                    p008 = parsed.get("P008"),
                    p009 = parsed.get("P009"),
                    p011 = parsed.get("P011"),
                    p012 = parsed.get("P012"),
                    p013 = parsed.get("P013"),
                    p014 = parsed.get("P014"),
                    p015 = parsed.get("P015"),
                    p016 = parsed.get("P016"),
                    p017 = parsed.get("P017"),
                    p018 = parsed.get("P018"),
                    p019 = parsed.get("P019"),
                    p021 = parsed.get("P021"),
                    p022 = parsed.get("P022"),
                    p023 = parsed.get("P023"),
                    p024 = parsed.get("P024"),
                    p025 = parsed.get("P025"),
                    p026 = parsed.get("P026"),
                    p027 = parsed.get("P027"),
                    p028 = parsed.get("P028"),
                    p029 = parsed.get("P029"),
                    p030 = parsed.get("P030"),
                    p031 = parsed.get("P031"),
                    p032 = parsed.get("P032"),
                    p033 = parsed.get("P033"),
                    p034 = parsed.get("P034"),
                    p035 = parsed.get("P035"),
                    p036 = parsed.get("P036"),
                    devType = parsed.get("DevType")):
                    if self.proxy.boilerTempCmd != boiler_temp or self.proxy.bBuModulMax != boiler_power:
                        self.send_command()
                    async_dispatcher_send(self.proxy._hass, SIGNAL_UPDATE)
                    
            except json.JSONDecodeError:
                _LOGGER.debug("[C] Waiting for full JSON chunk")
            finally:
                self.response_buffer = ""

        if self._remote_connected.is_set():
            self.remote_writer.write(data)
        else:
            _LOGGER.warning("Skipping forward: remote not connected")

    def send_command(self):
        if not all([self.proxy.serverToken, self.proxy.dev_id, self.proxy.dev_pin]):
            _LOGGER.warning("Empty Token/DevId/DevPin")
            return
        reply = {
            "FrameType": "DataToSen",
            "Token": self.proxy.serverToken,
            "DevId": self.proxy.dev_id,
            "DevPin": self.proxy.dev_pin,
            "BoilerTempCmd": self.proxy.boilerTempCmd or 6500,
            "BoilerHist": self.proxy.boilerHist or 200,
            "CH1Mode": "Still_On",
            "BuModulMax": self.proxy.buModulMax or 1
        }
        msg = json.dumps(reply)
        _LOGGER.info("→ Sending to client: %s", msg)
        if self.transport:
            self.transport.write(msg.encode())

    def update(self, **kwargs):
        updated = False
        for key, new_value in kwargs.items():
            if hasattr(self, key):
                current_value = getattr(self, key)
                if str(current_value) != str(new_value):
                    setattr(self, key, new_value)
                    updated = True

        return updated
    
