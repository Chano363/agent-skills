---
name: "mspm0-sysconfig-generator"
description: "Generate TI SysConfig files for MSPM0G3507 projects. Invoke when creating/modifying sysconfig files or configuring peripheral pins for MSPM0 projects."
---

# MSPM0 SysConfig Generator

This skill helps generate and modify TI SysConfig files for MSPM0G3507 projects, including proper pin allocation, peripheral configuration, and resource planning.

## Workflow

### Step 1: Pre-Analysis - Pin Allocation and Resource Planning

Before creating sysconfig, complete this planning table:

| Resource Type | Quantity | Required Pins/Features | Notes |
|---------------|----------|------------------------|-------|
| UART | | TX/RX pairs, interrupt | Check pinmux conflicts |
| I2C | | SCL/SDA, 400kHz | External pull-ups needed |
| PWM | | TimerG channels | 20kHz typical for motors |
| Timer | | Periodic interrupt | 1-100ms range |
| GPIO Input | | Pull-up/down, interrupt | Consider special pins |
| GPIO Output | | Push-pull/open-drain | Drive strength |
| QEI | | TIMG8/TIMG7 instances | Encoder interface |

### Step 2: Verify MSPM0G3507 Pin Constraints

**Critical Constraints:**
- LQFP-48 package: GPIOA (PA0-PA31), GPIOB (PB0-PB31) only - NO GPIOC/GPIOD
- PA0/PA1: Open-drain, 5V tolerant - MUST use external pull-up
- PA21/PA22: Default analog (VREF) - must disable external VREF
- PA23: VREF+ - can use as digital if VREF disabled
- Each GPIO instance can only target ONE port

### Step 3: Generate SysConfig Structure

Use this template structure:

```javascript
const GPIO = scripting.addModule("/ti/driverlib/GPIO", {}, false);
const GPIO_INSTANCE = GPIO.addInstance();
GPIO_INSTANCE.$name = "GROUP_NAME";
GPIO_INSTANCE.port = "PORTA"; // or PORTB
GPIO_INSTANCE.associatedPins.create(N);
```

### Step 4: Configure Peripherals

#### UART Configuration
```javascript
UART_INSTANCE.$name = "UART_NAME";
UART_INSTANCE.targetBaudRate = 115200;
UART_INSTANCE.enabledInterrupts = ["RX"];
UART_INSTANCE.interruptPriority = "2";
UART_INSTANCE.peripheral.txPin.$assign = "PA8";
UART_INSTANCE.peripheral.rxPin.$assign = "PA9";
```

#### I2C Configuration
```javascript
I2C_INSTANCE.$name = "I2C_NAME";
I2C_INSTANCE.basicEnableController = true;
I2C_INSTANCE.basicControllerStandardBusSpeed = "Fast"; // 400kHz
```

#### PWM Configuration
```javascript
PWM_INSTANCE.$name = "PWM_NAME";
PWM_INSTANCE.ccIndex = [0];
PWM_INSTANCE.timerStartTimer = true;
PWM_INSTANCE.clockDivider = 1;
PWM_INSTANCE.clockPrescale = 1;
PWM_INSTANCE.timerCount = 2000; // 40MHz/2000 = 20kHz
```

#### TIMER Configuration
```javascript
TIMER_INSTANCE.$name = "TIMER_NAME";
TIMER_INSTANCE.timerMode = "PERIODIC";
TIMER_INSTANCE.interrupts = ["ZERO"];
TIMER_INSTANCE.timerPeriod = "10 ms";
TIMER_INSTANCE.timerClkPrescale = 10; // Adjust for valid period
```

### Step 5: Add Pinmux Solutions

```javascript
UART_INSTANCE.peripheral.$suggestSolution = "UART1";
PWM_INSTANCE.peripheral.$suggestSolution = "TIMG12";
```

## Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `unknown property: targetBitRate` | Wrong I2C property | Use `basicControllerStandardBusSpeed` |
| `PA0 is no longer valid` | PA0/PA1 are open-drain | Remove internalResistor, add external pull-up |
| `PD3 is no longer valid` | PORTD doesn't exist | Use PA4-PA7 or PB pins |
| `Timer Period out of range` | Wrong clock prescale | Adjust `timerClkPrescale` |
| `Resource conflict` | Pin assigned to multiple peripherals | Check pinmux table |
| **`'RESET' is no longer valid`** | SDK 2.10 removed `"RESET"` value | Use `"LOW"` instead |
| **`Prescaler is not available for 32-bit Timers`** | TIMA0/TIMA1 are 32-bit, no prescaler | Set `clockPrescale = 1`, adjust `timerCount` |
| **`unknown property: clockPrescale` on TIMG** | TIMG timers use `clockDivider`, not `clockPrescale` | Use `clockDivider` for TIMG, `clockPrescale` only for TIMA |

## Critical Rules (Lessons Learned)

### Rule 1: ALL `addModule()` and `addInstance()` MUST be at the top

SysConfig requires a strict two-phase structure:
1. **Import phase** (top of file): ALL `scripting.addModule()` and `module.addInstance()` calls
2. **Configuration phase** (below): ALL property assignments (`$name`, `port`, `pin.$assign`, etc.)

**WRONG** — `Board` module declared in the middle of GPIO config:
```javascript
GPIO1.$name = "KEY";
// ... GPIO1 config ...

const Board = scripting.addModule("/ti/driverlib/Board", {}, false);  //  ERROR
Board.peripheral.$assign = "DEBUGSS";
```

**CORRECT** — All module declarations at the top:
```javascript
const GPIO  = scripting.addModule("/ti/driverlib/GPIO", {}, false);
const GPIO1 = GPIO.addInstance();
const Board = scripting.addModule("/ti/driverlib/Board", {}, false);  // ✅ at top
const I2C   = scripting.addModule("/ti/driverlib/I2C", {}, false);
const I2C1  = I2C.addInstance();
// ... all other addModule/addInstance calls ...

// Then configuration phase:
GPIO1.$name = "KEY";
Board.peripheral.$assign = "DEBUGSS";
I2C1.$name = "I2C_OLED";
```

### Rule 2: GPIO instances are per-port, not per-function

Each GPIO instance targets ONE port. If you need pins from both PORTA and PORTB, you need TWO instances.

```javascript
// WRONG: mixing ports in one instance
GPIO1.port = "PORTA";
GPIO1.associatedPins[0].pin.$assign = "PA2";   // PORTA ✅
GPIO1.associatedPins[1].pin.$assign = "PB6";   // PORTB ❌ ERROR

// CORRECT: separate instances per port
GPIO1.port = "PORTA";
GPIO1.associatedPins[0].pin.$assign = "PA2";

GPIO2.port = "PORTB";
GPIO2.associatedPins[0].pin.$assign = "PB6";
```

### Rule 3: Pin name determines macro suffix

SysConfig generates macros as `{GROUP}_{PIN}_PIN` and `{GROUP}_PORT`.

```javascript
GPIO6.$name = "ENC";
GPIO6.port = "PORTA";
GPIO6.associatedPins[0].$name = "LA";
GPIO6.associatedPins[0].pin.$assign = "PA21";
// Generates: ENC_PORT, ENC_LA_PIN ✅
```

If you need `ENC_LA_PIN` (not `ENC_LA_LA_PIN`), the pin `$name` should be `LA`, not `PIN`.

### Rule 4: 32-bit vs 16-bit timer properties differ

| Property | TIMA (32-bit) | TIMG (16-bit) |
|----------|--------------|---------------|
| Prescaler | `clockPrescale` (must be 1) | `clockDivider` |
| Count | `timerCount` | `timerCount` |
| Frequency formula | 32MHz / prescale / count | 32MHz / divider / count |

### Rule 5: Board module is separate from GPIO

`Board` (DEBUGSS) is its own module, not a GPIO instance. It must be declared with `scripting.addModule()` like any other peripheral.

```javascript
const Board = scripting.addModule("/ti/driverlib/Board", {}, false);
Board.peripheral.$assign = "DEBUGSS";
Board.peripheral.swclkPin.$assign = "PA20";
Board.peripheral.swdioPin.$assign = "PA19";
```

### Rule 6: GPIO interrupt polarity values

MSPM0 SysConfig uses specific string values for GPIO interrupt polarity:

| Value | Meaning |
|-------|---------|
| `"RISE"` | Rising edge only |
| `"FALL"` | Falling edge only |
| `"RISE_FALL"` | Both edges (rising AND falling) |

**WRONG**: `"BOTH"` — this value does not exist in MSPM0 SysConfig
**CORRECT**: `"RISE_FALL"` — for dual-edge interrupts (e.g., encoder A/B signals)

```javascript
// Encoder A/B phase needs both-edge interrupt
GPIO6.associatedPins[0].polarity = "RISE_FALL";  // ✅
// NOT: GPIO6.associatedPins[0].polarity = "BOTH";  // ❌ ERROR
```

## Reference Files

- [pinmux.md](references/pinmux.md) - MSPM0G3507 LQFP-48 pinmux table
- [properties.md](references/properties.md) - Valid property names for each module

## Assets

- [sysconfig-template.js](assets/sysconfig-template.js) - Complete template file

## Usage Example

```
User: "Generate sysconfig for MSPM0G3507 with UART1, I2C1, 2 PWM, and 8 GPIO inputs"

Agent: 
1. Ask for pin assignments
2. Validate against pinmux constraints
3. Generate sysconfig file
4. Add suggestSolution entries
```
