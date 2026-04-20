### status_bar_chip_temp_value
ESP32 internal chip temperature in "%.1f°C"

### status_bar_wifi_signal_icon
Adapt based on connection status.

    - Not connected:                        "U+F092B" // mdi:wifi-strength-alert-outline (disconnected)
    - Connected with RSSI in range 3/4-4/4: "U+F0928" // mdi:wifi-strength-4  (strong)
    - Connected with RSSI in range 2/4-3/4: "U+F0925" // mdi:wifi-strength-3  (medium)
    - Connected with RSSI in range 1/4-2/4: "U+F0922" // mdi:wifi-strength-2  (weak)
    - Connected with RSSI in range 0/4-1/4: "U+F091F" // mdi:wifi-strength-1  (very weak)

### status_bar_time_value
Current time in HH:MM:SS (24 hr)

### weather_date_value
Current date in mm/dd (no leading zero, for example 1/1, 12/31)

### weather_weekday_value
Current weekday in: Mon / Tue / Wed / Thu / Fri / Sat / Sun

### weather_outdoor_temp_value
HA `sensor.openweathermap_temperature` in "%.1f°C"

### weather_outdoor_humidity_value
HA `sensor.openweathermap_humidity` in "%.0f%%"

### weather_outdoor_sun_rise_value
HA `sensor.sun_next_rising` (UTC time) in HH:MM (local time)

### weather_outdoor_sun_set_value
HA `sensor.sun_next_setting` (UTC time) in HH:MM (local time)

### weather_outdoor_pressure_value
HA `sensor.openweathermap_pressure` in "%.0fhPa"

### server_room_left_value
HA `sensor.shellypmminig3_84fce63eb108_power` in "%.0fW"

### server_room_right_value
HA `sensor.server_room_temperature` in "%.1f°C"

### living_room_left_value
HA `sensor.shellypmminig3_ecda3bc6f94c_power` in "%.0fW"

### living_room_right_value
HA `sensor.living_room_current_temperature` in "%.1f°C"

### weater_outdoor_status_icon
Icon based on HA `sensor.openweathermap_weather_code`, rules:

```c++
auto weater_outdoor_status_icon_glyph = [](float code) -> const char* {
    int c = (int)code;
    if (c == 800)             return "\U000F0599"; // mdi:weather-sunny
    if (c >= 801 && c <= 803) return "\U000F0595"; // mdi:weather-partly-cloudy
    if (c == 804)             return "\U000F0590"; // mdi:weather-cloudy
    if (c >= 500 && c <= 531) return "\U000F0597"; // mdi:weather-rainy
    if (c >= 300 && c <= 321) return "\U000F0597"; // mdi:weather-rainy
    if (c >= 600 && c <= 622) return "\U000F0598"; // mdi:weather-snowy
    if (c >= 200 && c <= 232) return "\U000F0593"; // mdi:weather-lightning
    if (c >= 700 && c <= 781) 
        if (c == 781)         return "\U000F0F38"; // mdi:weather-tornado
        else                  return "\U000F0591"; // mdi:weather-fog
    return "\U000F0599";                           // mdi:weather-sunny
};
```

### MDI (Material Design Icons) lookup by name (name -> codepoint):
https://pictogrammers.com/library/mdi/