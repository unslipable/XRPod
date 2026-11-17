# Fan ESP32

ESP32-S3 sketch that drives the Corsair RS120 fans (4-pin PWM) and reads their speed.

- Board: "ESP32S3 Dev Module" in Arduino IDE (esp32 core 3.x).
- Wiring: fan pin 4 (PWM) to GPIO 4, fan pin 3 (tach) to GPIO 5, fan pin 1 (GND)
  to the 12 V supply's minus AND an ESP32 GND, fan pin 2 to 12 V plus.
  12 V never touches the ESP32.
- Put the Wi-Fi name and password in `fan.ino` before uploading. Don't commit them.
- API: `GET /fan?pct=0-100` sets the speed, `GET /status` reads it. Both return
  `{"fan_pct": 80, "fan_rpm": 1680}`. The board also answers as `xrpod-fan.local`.
- The Pi uses it when `FAN_ESP32_URL` is set (see `pi-agent/xrpod.service`).
