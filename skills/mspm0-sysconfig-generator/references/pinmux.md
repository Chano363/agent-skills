# MSPM0G3507 LQFP-48 Pinmux Table

## UART Pin Assignments

| UART | TX | RX | Alternative Functions |
|------|----|----|----------------------|
| UART0 | PA0 | PA1 | GPIO, I2C0 |
| UART1 | PA8 | PA9 | GPIO, SPI0 |
| UART2 | PA23 | PA24 | GPIO, ADC |
| UART3 | PA26 | PA25 | GPIO |

## I2C Pin Assignments

| I2C | SCL | SDA | Alternative Functions |
|-----|-----|-----|----------------------|
| I2C0 | PA1 | PA0 | GPIO, UART0 |
| I2C1 | PA17 | PA18 | GPIO |

## PWM/TimerG Pin Assignments

| TimerG | Channel 0 | Channel 1 |
|--------|-----------|-----------|
| TIMG6 | PB6 | PB7 |
| TIMG7 | PA28 | PA31 |
| TIMG8 | PA21 | PA22 |
| TIMG12 | PA14 | - |

## TimerA Pin Assignments

| TimerA | Channel 0 | Channel 1 |
|--------|-----------|-----------|
| TIMA0 | - | - |
| TIMA1 | PA15 | - |

## Special Pins

| Pin | Type | Notes |
|-----|------|-------|
| PA0 | Open-drain | 5V tolerant, needs external pull-up |
| PA1 | Open-drain | 5V tolerant, needs external pull-up |
| PA21 | Analog | VREF-/A1_7, must disable VREF for digital use |
| PA22 | Analog | VREF-/A0_7, must disable VREF for digital use |
| PA23 | Analog | VREF+, must disable VREF for digital use |

## Pin Availability

**GPIOA:** PA0-PA31 (all available in LQFP-48)
**GPIOB:** PB0-PB31 (all available in LQFP-48)
**GPIOC:** NOT available in LQFP-48
**GPIOD:** NOT available in LQFP-48

## Pinmux Rules

1. Each pin can only be assigned to one peripheral function at a time
2. PA0/PA1 default to UART0 - reassign only if UART0 is not used
3. PA21/PA22/PA23 are analog by default - configure as digital in SysConfig
4. Debug pins (PA19/PA20) are used for SWD - avoid reassigning
