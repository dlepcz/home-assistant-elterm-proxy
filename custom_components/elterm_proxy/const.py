from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntityDescription,
    BinarySensorEntityDescription,
    SensorStateClass
)

from homeassistant.components.binary_sensor import (
    BinarySensorEntityDescription,
)

from homeassistant.const import (
    PERCENTAGE,
    UnitOfTemperature,
)
from homeassistant.components.select import SelectEntityDescription
from homeassistant.components.number import NumberEntityDescription, NumberDeviceClass, NumberMode
from dataclasses import dataclass

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
ELTERM_DATA: dict[str, str] =  {
    "DevId" : "Identifier",
    "DevPin" : "PIN",
    "Token" : "Token",
    "FrameType" : "Frame type",
    "TimeStamp" : "Timestamp",
    "DevStatus" : "Status",
    "Alarms" : "Alarms",
    "BoilerTempAct" : "Actual temperature",
    "BoilerTempCmd" : "Set temperature",
    "BoilerHist" : "Hysteresis central heating",
    "DHWTempAct" : "DHWTempAct",
    "DHWTempCmd" : "DHWTempCmd",
    "DHWOverH" : "DHWOverH",
    "DHWHist" : "DHWHist",
    "DHWMode" : "DHWMode",
    "CH1RoomTempAct" : "CH1RoomTempAct",
    "CH1RoomTempCom" : "CH1RoomTempCom",
    "CH1RoomTempCmd" : "CH1RoomTempCmd",
    "CH1RoomHist" : "CH1RoomHist",
    "CH1Mode" : "CH1Mode",
    "WeaTempAct" : "WeaTempAct",
    "WeaCorr" : "WeaCorr",
    "UpTime" : "UpTime",
    "BuModulMax" : "Set power",
    "P001" : "P001",
    "P002" : "P002",
    "P003" : "P003",
    "P004" : "P004",
    "P005" : "P005",
    "P006" : "P006",
    "P007" : "P007",
    "P008" : "P008",
    "P009" : "P009",
    "P011" : "P011",
    "P012" : "P012",
    "P013" : "P013",
    "P014" : "P014",
    "P015" : "P015",
    "P016" : "P016",
    "P017" : "P017",
    "P018" : "P018",
    "P019" : "P019",
    "P021" : "P021",
    "P022" : "P022",
    "P023" : "P023",
    "P024" : "P024",
    "P025" : "P025",
    "P026" : "P026",
    "P027" : "P027",
    "P028" : "P028",
    "P029" : "P029",
    "P030" : "P030",
    "P031" : "P031",
    "P032" : "P032",
    "P033" : "P033",
    "P034" : "P034",
    "P035" : "P035",
    "P036" : "P036",
    "DevType" : "Type",
    "boilerStatus" : "Boiler status",
    "serverToken" : "Server token",
}

@dataclass
class EltermSelectDescriptionMixin:
    options_dict: dict[int, str]


@dataclass
class EltermSelectDescription(
    SelectEntityDescription, EltermSelectDescriptionMixin
):
    """Class to describe an elterm select entity."""

@dataclass
class EltermNumberDescriptionMixin:
    attrs: dict


@dataclass
class EltermNumberDescription(
    NumberEntityDescription, EltermNumberDescriptionMixin
):
    """Class to describe an elterm select entity."""

ELTERM_CONTROL_TEMP = {
    "setBoilerTempCmd" : "Temperature",
}

ELTERM_CONTROL_POWER = {
    "setBuModulMax" : "Power",
}

ELTERM_CONTROL_POWER_MODE = {
    "0": "33%",
    "1": "67%",
    "2": "100%",
}

ELTERM_BINARY = {
    "pumpIsRunning" : "Pump is running",
}

ELTERM_SENSORS: list[SensorEntityDescription] = []

for key, value in ELTERM_DATA.items():
    if "Temp" in key:
        ELTERM_SENSORS.append(
            SensorEntityDescription(
                key=key,
                name=value,
                device_class=SensorDeviceClass.TEMPERATURE,
                native_unit_of_measurement=UnitOfTemperature.CELSIUS,
                state_class=SensorStateClass.MEASUREMENT,
            )
        )
    else:
        ELTERM_SENSORS.append(
            SensorEntityDescription(
                key=key,
                name=value,
            )
        )

ELTERM_BINARY_SENSORS: list[BinarySensorEntityDescription] = []

for key, value in ELTERM_BINARY.items():
    ELTERM_BINARY_SENSORS.append(
        BinarySensorEntityDescription(
                key=key,
                name=value,
            )
    )

ELTERM_CONTROL_SELECT: list[EltermSelectDescription] = []

for key, value in ELTERM_CONTROL_POWER.items():
    ELTERM_CONTROL_SELECT.append(
        EltermSelectDescription(
            key=key,
            name=value,
            options_dict=ELTERM_CONTROL_POWER_MODE,
        )
    )

ELTERM_CONTROL_TEMPERATURE: list[EltermNumberDescription] = []

for key, value in ELTERM_CONTROL_TEMP.items():
    ELTERM_CONTROL_TEMPERATURE.append(
        EltermNumberDescription(
            key=key,
            name=value,
            attrs={"min": 20, "max": 70, "default": 65, "step": 1},
            native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            device_class=NumberDeviceClass.TEMPERATURE,
            mode=NumberMode.BOX,
        )
    )