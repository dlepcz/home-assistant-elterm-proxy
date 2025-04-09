[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)

# 🏭 Elterm TCP Proxy for Home Assistant

**Elterm Proxy** is a fully-featured Home Assistant integration that acts as a full-duplex TCP proxy between a Elterm electric boiler and Elterm server. Integration captures TCP data and create entities for Home Assistant and allow control boiler parameters.

The integration enables:
- Real-time data interception and analysis (e.g., temperature, mode, token).
- Sending control commands to the boiler (e.g., target temperature, mode).
- Dynamic creation of `sensor` entities.
- Control `number` and `select` entities.
- Configuration via Home Assistant UI (config flow).
- Full support of the Elterm data model (`BoilerTempAct`, `CH1Mode`, `Token`, `BuModulMax`, etc.).

---

## ⚙️ Features

- 🔌 **Full TCP Proxy**: relays traffic between client and Elterm device.
- 🔁 **JSON Analysis & Injection**: parses and modifies traffic live.
- 🧠 **Dynamic Entity Creation**:
  - `sensor.elterm_*`
  - `number.elterm_temperature` – set boiler temperature
  - `select.elterm_power` – set power output (33%, 67%, 100%)
- 📡 **Automatic token detection and forwarding**
- 🧰 **Configurable via UI or YAML**

---

## 🧰 Requirements

- Home Assistant 2023.12 or newer
- Python 3.11+
- Elterm boiler with TCP communication support
- Access to device IP and port

---

## 🔧 Installation

### 1. Using HACS (recommended)
1. Open HACS > Integrations > Add Custom Repository
2. Enter the repo URL: https://github.com/dlepcz/home-assistant-elterm-proxy
3. Select `Integration` type
4. Install and restart Home Assistant

### 2. Manual
Copy the `elterm_proxy` folder to: /config/custom_components/elterm_proxy/

---

## 🚀 Configuration

### Via Home Assistant UI
1. Go to **Settings > Devices & Services**
2. Click `+ Add Integration`, search for `Elterm Proxy`
3. Fill in:
   - `Listen port` (e.g., 9999)
   - `Forward host` (e.g., 46.242.129.11)
   - `Forward port` (e.g., 88)
   - `DevId` and `DevPin` (as per your boiler setup)

After saving, TCP proxy will be started and entities created automatically.

---

## 📈 Entities

### 🧪 Sensors
- `sensor.elterm_boiler_temp` – current boiler temperature
- `sensor.elterm_boiler_power` – current power level
- `sensor.elterm_boiler_token` – current session token

### 🎛️ Control entities
- `number.elterm_temperature` – temperature setpoint (20–70°C)
- `select.elterm_power` – power mode (33%, 67%, 100%)

---
Settings > System > Logs
Look for entries prefixed with: [custom_components.elterm_proxy.proxy]

🙌 Author
Created by @dlepcz.
"Elterm" is a trademark of the boiler manufacturer.


📃 License
This project is open-source under the MIT license.
Use at your own risk. Test it thoroughly before using in production with real heating hardware.


