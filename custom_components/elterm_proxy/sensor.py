import logging
from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.dispatcher import async_dispatcher_connect
from .const import DOMAIN, SIGNAL_UPDATE

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass, config_entry, async_add_entities):
    proxy = hass.data[DOMAIN][config_entry.entry_id]
    sensors = [
        EltermProxySensor(proxy, "elterm_devId"),
        EltermProxySensor(proxy, "elterm_devPin"),
        EltermProxySensor(proxy, "elterm_token"),
        EltermProxySensor(proxy, "elterm_serverToken"),
        EltermProxySensor(proxy, "elterm_frameType"),
        EltermProxySensor(proxy, "elterm_timeStamp"),
        EltermProxySensor(proxy, "elterm_devStatus", "Elterm boiler status"),
        EltermProxySensor(proxy, "elterm_pumpStatus", "Elterm pump status"),
        EltermProxySensor(proxy, "elterm_alarms"),
        EltermProxySensor(proxy, "elterm_boilerTempAct", "", "°C", "temperature", 100),
        EltermProxySensor(proxy, "elterm_boilerTempCmd", "", "°C", "temperature", 100),
        EltermProxySensor(proxy, "elterm_boilerHist", "", "°C", "temperature", 100),
        EltermProxySensor(proxy, "elterm_dHWTempAct", "", "°C", "temperature", 100),
        EltermProxySensor(proxy, "elterm_dHWTempCmd", "", "°C", "temperature", 100),
        EltermProxySensor(proxy, "elterm_dHWOverH"),
        EltermProxySensor(proxy, "elterm_dHWHist"),
        EltermProxySensor(proxy, "elterm_dHWMode"),
        EltermProxySensor(proxy, "elterm_cH1RoomTempAct", "", "°C", "temperature", 100),
        EltermProxySensor(proxy, "elterm_cH1RoomTempCom", "", "°C", "temperature", 100),
        EltermProxySensor(proxy, "elterm_cH1RoomTempCmd", "", "°C", "temperature", 100),
        EltermProxySensor(proxy, "elterm_cH1RoomHist"),
        EltermProxySensor(proxy, "elterm_cH1Mode"),
        EltermProxySensor(proxy, "elterm_weaTempAct", "", "°C", "temperature", 100),
        EltermProxySensor(proxy, "elterm_weaCorr"),
        EltermProxySensor(proxy, "elterm_upTime", "", "","duration"),
        EltermProxySensor(proxy, "elterm_buModulMax", "Elterm max power", "%"),
        EltermProxySensor(proxy, "elterm_buModulCurr", "Elterm current power", "%"),
        EltermProxySensor(proxy, "elterm_p001"),
        EltermProxySensor(proxy, "elterm_p002"),
        EltermProxySensor(proxy, "elterm_p003"),
        EltermProxySensor(proxy, "elterm_p004"),
        EltermProxySensor(proxy, "elterm_p005"),
        EltermProxySensor(proxy, "elterm_p006"),
        EltermProxySensor(proxy, "elterm_p007"),
        EltermProxySensor(proxy, "elterm_p008"),
        EltermProxySensor(proxy, "elterm_p009"),
        EltermProxySensor(proxy, "elterm_p011"),
        EltermProxySensor(proxy, "elterm_p012"),
        EltermProxySensor(proxy, "elterm_p013"),
        EltermProxySensor(proxy, "elterm_p014"),
        EltermProxySensor(proxy, "elterm_p015"),
        EltermProxySensor(proxy, "elterm_p016"),
        EltermProxySensor(proxy, "elterm_p017"),
        EltermProxySensor(proxy, "elterm_p018"),
        EltermProxySensor(proxy, "elterm_p019"),
        EltermProxySensor(proxy, "elterm_p021"),
        EltermProxySensor(proxy, "elterm_p022"),
        EltermProxySensor(proxy, "elterm_p023"),
        EltermProxySensor(proxy, "elterm_p024"),
        EltermProxySensor(proxy, "elterm_p025"),
        EltermProxySensor(proxy, "elterm_p026"),
        EltermProxySensor(proxy, "elterm_p027"),
        EltermProxySensor(proxy, "elterm_p028"),
        EltermProxySensor(proxy, "elterm_p029"),
        EltermProxySensor(proxy, "elterm_p030"),
        EltermProxySensor(proxy, "elterm_p031"),
        EltermProxySensor(proxy, "elterm_p032"),
        EltermProxySensor(proxy, "elterm_p033"),
        EltermProxySensor(proxy, "elterm_p034"),
        EltermProxySensor(proxy, "elterm_p035"),
        EltermProxySensor(proxy, "elterm_p036"),
        EltermProxySensor(proxy, "elterm_devType")
    ]
    async_add_entities(sensors)

    async def handle_update():
        for sensor in sensors:
            sensor.update_state()
            sensor.async_schedule_update_ha_state()

    async_dispatcher_connect(hass, SIGNAL_UPDATE, handle_update)


class EltermProxySensor(SensorEntity):
    def __init__(self, proxy, key, name = "", unit = None, deviceClass = None, scale = None):
        self._proxy = proxy
        self._key = key
        self._name = name
        self._unit = unit
        self._deviceClass = deviceClass
        self._scale = scale
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
    def unit_of_measurement(self):
        return self._unit
        
    @property
    def device_class(self):
        return self._deviceClass
    
    @property
    def unique_id(self):
        return f"{self._proxy.name}_{self._key}"

    @property
    def state(self):
        value = self.hass.data[DOMAIN]["values"].get(self._key)
        if self._scale != None:
            try:
                return int(value) / self._scale
            except:
                return value
            
        return value

    def update_state(self):
        _LOGGER.debug("Update sensor %s", self._key)
        match self._key:
            case "elterm_devId": 
                self._state = self._proxy.devId
            case "elterm_devPin":
                self._state = self._proxy.devPin
            case "elterm_token": 
                self._state = self._proxy.token
            case "elterm_serverToken": 
                self._state = self._proxy.serverToken
            case "elterm_frameType": 
                self._state = self._proxy.frameType
            case "elterm_timeStamp": 
                self._state = self._proxy.timeStamp
            case "elterm_devStatus": 
                self._state = self._proxy.devStatus
            case "elterm_pumpStatus":
                self._state = self._proxy.devStatus[10:11]
            case "elterm_alarms":
                self._state = self._proxy.alarms
            case "elterm_boilerTempAct": 
                self._state = self._proxy.boilerTempAct
            case "elterm_boilerTempCmd": 
                self._state = self._proxy.boilerTempCmd
            case "elterm_boilerHist": 
                self._state = self._proxy.boilerHist
            case "elterm_dHWTempAct": 
                self._state = self._proxy.dHWTempAct
            case "elterm_dHWTempCmd": 
                self._state = self._proxy.dHWTempCmd
            case "elterm_dHWOverH": 
                self._state = self._proxy.dHWOverH
            case "elterm_dHWHist": 
                self._state = self._proxy.dHWHist
            case "elterm_dHWMode": 
                self._state = self._proxy.dHWMode
            case "elterm_cH1RoomTempAct": 
                self._state = self._proxy.cH1RoomTempAct
            case "elterm_cH1RoomTempCom": 
                self._state = self._proxy.cH1RoomTempCom
            case "elterm_cH1RoomTempCmd": 
                self._state = self._proxy.cH1RoomTempCmd
            case "elterm_cH1RoomHist": 
                self._state = self._proxy.cH1RoomHist
            case "elterm_cH1Mode": 
                self._state = self._proxy.cH1Mode
            case "elterm_weaTempAct": 
                self._state = self._proxy.weaTempAct
            case "elterm_weaCorr": 
                self._state = self._proxy.weaCorr
            case "elterm_upTime": 
                self._state = self._proxy.upTime
            case "elterm_buModulMax": 
                match self._proxy.buModulMax:
                    case "0":
                        self._state = "33"
                    case "1":
                        self._state = "67"
                    case "2":
                        self._state = "100"
                    case _:
                        self._state = "0"    
            case "elterm_buModulCurr":
                self._state = self._proxy.devStatus[3:6]
            case "elterm_p001": 
                self._state = self._proxy.p001
            case "elterm_p002": 
                self._state = self._proxy.p002
            case "elterm_p003": 
                self._state = self._proxy.p003
            case "elterm_p004": 
                self._state = self._proxy.p004
            case "elterm_p005": 
                self._state = self._proxy.p005
            case "elterm_p006": 
                self._state = self._proxy.p006
            case "elterm_p007": 
                self._state = self._proxy.p007
            case "elterm_p008": 
                self._state = self._proxy.p008
            case "elterm_p009": 
                self._state = self._proxy.p009
            case "elterm_p011": 
                self._state = self._proxy.p011
            case "elterm_p012": 
                self._state = self._proxy.p012
            case "elterm_p013": 
                self._state = self._proxy.p013
            case "elterm_p014": 
                self._state = self._proxy.p014
            case "elterm_p015": 
                self._state = self._proxy.p015
            case "elterm_p016": 
                self._state = self._proxy.p016
            case "elterm_p017": 
                self._state = self._proxy.p017
            case "elterm_p018": 
                self._state = self._proxy.p018
            case "elterm_p019": 
                self._state = self._proxy.p019
            case "elterm_p021": 
                self._state = self._proxy.p021
            case "elterm_p022": 
                self._state = self._proxy.p022
            case "elterm_p023": 
                self._state = self._proxy.p023
            case "elterm_p024": 
                self._state = self._proxy.p024
            case "elterm_p025": 
                self._state = self._proxy.p025
            case "elterm_p026": 
                self._state = self._proxy.p026
            case "elterm_p027": 
                self._state = self._proxy.p027
            case "elterm_p028": 
                self._state = self._proxy.p028
            case "elterm_p029": 
                self._state = self._proxy.p029
            case "elterm_p030": 
                self._state = self._proxy.p030
            case "elterm_p031": 
                self._state = self._proxy.p031
            case "elterm_p032": 
                self._state = self._proxy.p032
            case "elterm_p033": 
                self._state = self._proxy.p033
            case "elterm_p034": 
                self._state = self._proxy.p034
            case "elterm_p035": 
                self._state = self._proxy.p035
            case "elterm_p036": 
                self._state = self._proxy.p036
            case "elterm_devType": 
                self._state = self._proxy.devType 