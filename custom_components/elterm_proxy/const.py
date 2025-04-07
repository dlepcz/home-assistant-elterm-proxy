from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    SensorStateClass,
)

from homeassistant.const import (
    PERCENTAGE,
    UnitOfTemperature,
)

DOMAIN = "elterm_proxy"
DEFAULT_NAME = "elterm"
DEFAULT_LISTEN_PORT = 9999
DEFAULT_FORWARD_HOST = "46.242.129.11"
DEFAULT_FORWARD_PORT = 88
DEFAULT_DEV_ID = "XXXX"
DEFAULT_DEV_PIN = "XXXX"
SIGNAL_UPDATE = f"{DOMAIN}_update"
UPDATE_INTERVAL=30
ATTR_MANUFACTURER = "Elterm"
ELTERM_DATA = [
    "DevId",
    "DevPin",
    "Token",
    "FrameType",
    "TimeStamp",
    "DevStatus",
    "Alarms",
    "BoilerTempAct",
    "BoilerTempCmd",
    "BoilerHist",
    "DHWTempAct",
    "DHWTempCmd",
    "DHWOverH",
    "DHWHist",
    "DHWMode",
    "CH1RoomTempAct",
    "CH1RoomTempCom",
    "CH1RoomTempCmd",
    "CH1RoomHist",
    "CH1Mode",
    "WeaTempAct",
    "WeaCorr",
    "UpTime",
    "BuModulMax",
    "P001",
    "P002",
    "P003",
    "P004",
    "P005",
    "P006",
    "P007",
    "P008",
    "P009",
    "P011",
    "P012",
    "P013",
    "P014",
    "P015",
    "P016",
    "P017",
    "P018",
    "P019",
    "P021",
    "P022",
    "P023",
    "P024",
    "P025",
    "P026",
    "P027",
    "P028",
    "P029",
    "P030",
    "P031",
    "P032",
    "P033",
    "P034",
    "P035",
    "P036",
    "DevType",
]

ELTERM_SENSORS: list[SensorEntityDescription] = []

for d in ELTERM_DATA:
    if "Temp" in d:
        ELTERM_SENSORS.append(
            SensorEntityDescription(
                key=d.lower,
                name=d,
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=UnitOfTemperature.CELSIUS,
                state_class=SensorStateClass.MEASUREMENT,
            )
        )
    elif "BuModulMax" in d:
        ELTERM_SENSORS.append(
            SensorEntityDescription(
                key=d.lower,
                name=d,
                device_class=SensorDeviceClass.POWER_FACTOR,
                native_unit_of_measurement=PERCENTAGE,
                state_class=SensorStateClass.MEASUREMENT,
            )
        )
    else:
        ELTERM_SENSORS.append(
            SensorEntityDescription(
                key=d.lower,
                name=d,
                state_class=SensorStateClass.MEASUREMENT,
            )
        )
    