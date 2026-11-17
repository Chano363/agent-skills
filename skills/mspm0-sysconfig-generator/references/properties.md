# MSPM0 SysConfig Property Reference

## GPIO Module Properties

### Instance Properties
| Property | Type | Values | Description |
|----------|------|--------|-------------|
| `$name` | string | Any | User label name |
| `port` | string | "PORTA", "PORTB" | GPIO port |
| `associatedPins.create(N)` | method | N=number of pins | Create N pins |

### Pin Properties
| Property | Type | Values | Description |
|----------|------|--------|-------------|
| `$name` | string | Any | Pin label |
| `direction` | string | "INPUT", "OUTPUT" | Direction |
| `polarity` | string | "RISING", "FALL", "BOTH" | Interrupt trigger |
| `internalResistor` | string | "PULL_UP", "PULL_DOWN", "NONE" | Internal resistor |
| `interruptEn` | bool | true, false | Enable interrupt |
| `interruptPriority` | string | "0"-"7" | Interrupt priority |
| `pin.$assign` | string | "PA0", "PB1", etc. | Pin assignment |
| `initialValue` | string | "SET", "CLEAR" | Initial output value |

## UART Module Properties

### Instance Properties
| Property | Type | Values | Description |
|----------|------|--------|-------------|
| `$name` | string | Any | User label name |
| `targetBaudRate` | number | 9600-921600 | Baud rate |
| `enabledInterrupts` | array | ["RX", "TX", "ERROR"] | Enabled interrupts |
| `interruptPriority` | string | "0"-"7" | Interrupt priority |
| `peripheral.$assign` | string | "UART0"-"UART5" | UART instance |

### Pin Properties
| Property | Type | Values | Description |
|----------|------|--------|-------------|
| `peripheral.txPin.$assign` | string | Pin name | TX pin |
| `peripheral.rxPin.$assign` | string | Pin name | RX pin |
| `txPinConfig.direction` | string | "OUTPUT" | TX direction |
| `rxPinConfig.internalResistor` | string | "PULL_UP", "NONE" | RX pull-up |

## I2C Module Properties

### Instance Properties
| Property | Type | Values | Description |
|----------|------|--------|-------------|
| `$name` | string | Any | User label name |
| `basicEnableController` | bool | true, false | Enable controller mode |
| `basicControllerStandardBusSpeed` | string | "Standard", "Fast", "FastPlus" | Bus speed |
| `peripheral.$assign` | string | "I2C0", "I2C1" | I2C instance |

### Bus Speed Values
| Value | Speed |
|-------|-------|
| "Standard" | 100kHz |
| "Fast" | 400kHz |
| "FastPlus" | 1MHz |

## PWM Module Properties

### Instance Properties
| Property | Type | Values | Description |
|----------|------|--------|-------------|
| `$name` | string | Any | User label name |
| `ccIndex` | array | [0], [1], [0,1] | Capture/compare channels |
| `timerStartTimer` | bool | true, false | Auto-start timer |
| `clockDivider` | number | 1, 2, 4, 8 | Clock divider |
| `clockPrescale` | number | 1-256 | Clock prescaler |
| `timerCount` | number | 1-65535 | Timer period count |

### Pin Properties
| Property | Type | Values | Description |
|----------|------|--------|-------------|
| `peripheral.ccp0Pin.$assign` | string | Pin name | Channel 0 pin |
| `peripheral.ccp1Pin.$assign` | string | Pin name | Channel 1 pin |

### Frequency Calculation
```
Frequency = PeripheralClock / (clockDivider * clockPrescale * timerCount)
Example: 40MHz / (1 * 1 * 2000) = 20kHz
```

## TIMER Module Properties

### Instance Properties
| Property | Type | Values | Description |
|----------|------|--------|-------------|
| `$name` | string | Any | User label name |
| `timerMode` | string | "PERIODIC", "ONE_SHOT", "QEI" | Timer mode |
| `interrupts` | array | ["ZERO"] | Enabled interrupts |
| `timerPeriod` | string | "1 ms", "5 ms", "10 ms", etc. | Period |
| `timerClkDiv` | number | 1, 2, 4, 8 | Clock divider |
| `timerClkPrescale` | number | 1-256 | Clock prescaler |
| `timerStartTimer` | bool | true, false | Auto-start timer |
| `peripheral.$assign` | string | "TIMA0", "TIMA1", "TIMG6"-"TIMG12" | Timer instance |

### QEI Mode Properties (TimerG only)
| Property | Type | Values | Description |
|----------|------|--------|-------------|
| `timerMode` | string | "QEI" | Set to QEI mode |
| `ccIndex` | array | [0, 1] | Both channels |

## SYSCTL Module Properties

| Property | Type | Values | Description |
|----------|------|--------|-------------|
| `forceDefaultClkConfig` | bool | true | Use default clock |
| `clockTreeEn` | bool | true | Enable clock tree |

## SYSTICK Module Properties

| Property | Type | Values | Description |
|----------|------|--------|-------------|
| `periodEnable` | bool | true | Enable periodic mode |
| `systickEnable` | bool | true | Enable SysTick |
| `interruptPriority` | string | "0"-"7" | Priority |
| `period` | number | 1-255 | Period in ms |

## Board Module Properties

| Property | Type | Values | Description |
|----------|------|--------|-------------|
| `peripheral.$assign` | string | "DEBUGSS" | Debug interface |
| `peripheral.swclkPin.$assign` | string | "PA20" | SWCLK pin |
| `peripheral.swdioPin.$assign` | string | "PA19" | SWDIO pin |
