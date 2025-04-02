# Elterm TCP Proxy for Home Assistant

This custom integration creates a full TCP proxy between a local client and a remote Elterm boiler controller.

It allows Home Assistant to:
- Forward data bidirectionally over TCP,
- Dynamically read and modify boiler commands (`BoilerTempCmd`, `BoilerPowerCmd`),
- Inject updated values based on Home Assistant sensors,
- Expose proxy data as HA sensors (`boiler_temp`, `boiler_power`).

---

## 🔧 Features

- Full duplex TCP proxy
- JSON analysis and injection (including Token)
- Command control via Home Assistant
- Dynamic sensors for current temp and power
- Configurable via Home Assistant UI

---

## 🧰 Configuration

### Through UI
1. Go to `Settings > Devices & Services`
2. Click `+ Add Integration` > search for **Elterm Proxy**
3. Fill in required fields:
   - Listen port
   - Forward host and port
   - Device ID and PIN

---

## 📡 Controlling Boiler Setpoints

Add the following to your `configuration.yaml` or split files:

```yaml
input_number:
  boiler_temp_cmd:
    name: Boiler Temperature Setpoint
    min: 30
    max: 90
    step: 0.5
    unit_of_measurement: "°C"

  boiler_power_cmd:
    name: Boiler Power Setpoint
    min: 0
    max: 100
    step: 1
    unit_of_measurement: "%"

sensor:
  - platform: template
    sensors:
      boiler_temp_cmd:
        value_template: "{{ states('input_number.boiler_temp_cmd') | int }}"
        unit_of_measurement: "°C"

      boiler_power_cmd:
        value_template: "{{ states('input_number.boiler_power_cmd') | int }}"
        unit_of_measurement: "%"
