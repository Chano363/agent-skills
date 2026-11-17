# ESP32 DevKitC Pinout Verified

Commonly used pins for the project's K230-ESP32 link:

## K230 → ESP32 SPI Wiring

| Signal | K230 (SPI Master) | ESP32 (SPI Slave) | Notes |
|--------|------------------:|------------------:|:------|
| MOSI   | IO16              | GPIO13            | |
| MISO   | IO17              | GPIO12            | GPIO12 is strapping; do not pull high at boot |
| SCLK   | IO15              | GPIO14            | |
| CS     | IO14              | GPIO15            | |

## ESP32 DevKitC Pin Table

| GPIO | Strapping | Safe for Output | Notes |
|:----:|:---------:|:---------------:|:------|
| 0    | Boot mode | No (pull at boot) | LOW=download, HIGH=run |
| 1    | No        | Yes              | Also UART0 TX |
| 2    | No        | Yes              | Onboard LED (LOW=on) |
| 3    | No        | No (RX only)     | Also UART0 RX |
| 4    | No        | Yes              | Safe general purpose |
| 5    | No        | Yes              | Safe general purpose |
| 12   | Voltage   | Yes              | Pull HIGH = 3.3V → VDD_SDIO |
| 13   | No        | Yes              | SPI MOSI (Slave) |
| 14   | No        | Yes              | SPI SCLK (Slave) |
| 15   | No        | Yes              | SPI CS (Slave) |
| 16   | No        | Yes              | Safe general purpose |
| 17   | No        | Yes              | Safe general purpose |
| 18   | No        | Yes              | Safe general purpose |
| 19   | No        | Yes              | Safe general purpose |
| 21   | No        | Yes              | I2C SDA typical |
| 22   | No        | Yes              | I2C SCL typical |
| 23   | No        | Yes              | Safe general purpose |
| 25   | No        | Yes              | DAC output capable |
| 26   | No        | Yes              | Safe general purpose |
| 27   | No        | Yes              | Safe general purpose |
| 32   | No        | Yes              | ADC1_CH4 |
| 33   | No        | Yes              | ADC1_CH5 |
| 34   | No        | Input only       | ADC1_CH6 |
| 35   | No        | Input only       | ADC1_CH7 |
| 36   | No        | Input only       | ADC1_CH0 (SENSOR_VP) |
| 39   | No        | Input only       | ADC1_CH3 (SENSOR_VN) |

## Warnings

- **GPIO 12** is strapping: its voltage at boot sets the VDD_SDIO voltage (3.3V vs 1.8V).
  Do not use as a HIGH output at boot if the module expects 3.3V VDD_SDIO.
- **GPIO 0** must be HIGH for normal boot; pulled LOW for download mode.
- **GPIO 1 & 3** are UART0 (console). Reassign only if console is moved to another UART.
- Do not use **GPIO 6-11** (flash SPI) for general purpose on standard modules.
- Maximum safe output current: 40 mA per pin, 200 mA total across all pins.

## Pins chosen for wifi_tx project

| Function | GPIO |
|----------|:----:|
| SPI Slave MOSI | 13 |
| SPI Slave MISO | 12 |
| SPI Slave SCLK | 14 |
| SPI Slave CS   | 15 |
| UART console   | 1 (TX), 3 (RX) |
| WiFi antenna   | internal PCB trace |
