---
name: "ccs-build"
description: "Build and debug MSPM0 projects using CCS tiarmclang command-line compiler. Invoke when compiling MSPM0G3507 firmware outside CCS IDE, fixing build errors, or setting up command-line build workflows."
---

# CCS Command-Line Build for MSPM0G3507

Build and debug MSPM0G3507 firmware using TI ARM Clang (tiarmclang) from the command line, without requiring the CCS IDE GUI.

## Toolchain Location

```
CCS_ROOT = E:\ti\ccs\ccs_base\compiler\ti-cgt-armclang_5.1.1.LTS
COMPILER = ${CCS_ROOT}\bin\tiarmclang.exe
```

## Compiler Flags

### Mandatory Flags (MSPM0G3507 Cortex-M0+)

```
-march=thumbv6m
-mcpu=cortex-m0plus
-mfloat-abi=soft
-mthumb
-mlittle-endian
-gdwarf-3
-Wall
-O2
```

### Predefined Macros (from device.opt)

```
-D__MSPM0G3507__
-D__USE_SYSCONFIG__
```

These are stored in `Debug/device.opt` (one per line, `-D` prefix). Without these, DriverLib headers will fail with `DeviceFamily_XYZ` undefined errors.

### Include Paths

**SDK paths** (adjust SDK install dir):
```
-I${SDK_INSTALL_DIR}/source                    # DriverLib headers
-I${SDK_INSTALL_DIR}/source/third_party/CMSIS/Core/Include  # CMSIS core
```

**Project paths**:
```
-I${PROJECT_ROOT}            # empty.c, main header
-I${PROJECT_ROOT}/Debug      # ti_msp_dl_config.h (SysConfig generated)
-I${PROJECT_ROOT}/App        # Application layer
-I${PROJECT_ROOT}/Bsp        # Board support layer
-I${PROJECT_ROOT}/Drv        # Driver layer
-I${PROJECT_ROOT}/Lib        # Library layer
```

## Build Workflow

### Step 1: Run SysConfig to generate peripheral config

```powershell
$sysconfig = "E:\ti\sysconfig_1.26.2\sysconfig_cli.bat"
$sdkMeta = "E:\ti\mspm0_sdk_2_10_00_04\.metadata\product.json"
& $sysconfig -s $sdkMeta --script "path\to\empty.syscfg" -o "Debug" --compiler ticlang
```

This generates `Debug/ti_msp_dl_config.c` and `Debug/ti_msp_dl_config.h`.

### Step 2: Compile all .c files

```powershell
$cc = "E:\ti\ccs\ccs_base\compiler\ti-cgt-armclang_5.1.1.LTS\bin\tiarmclang.exe"
$sdk = "E:\ti\mspm0_sdk_2_10_00_04"

$defines = "-D__MSPM0G3507__", "-D__USE_SYSCONFIG__"
$targetFlags = "-march=thumbv6m", "-mcpu=cortex-m0plus", "-mfloat-abi=soft", "-mthumb", "-mlittle-endian", "-gdwarf-3", "-Wall", "-O2"

$includes = @(
    "-I$($sdk)\source",
    "-I$($sdk)\source\third_cmsis\CMSIS\Core\Include",
    "-I$projectRoot",
    "-I$projectRoot\Debug",
    "-I$projectRoot\App",
    "-I$projectRoot\Bsp",
    "-I$projectRoot\Drv",
    "-I$projectRoot\Lib"
)

Get-ChildItem -Recurse -Filter *.c -Path $projectRoot |
  Where-Object { $_.DirectoryName -notmatch "Release" } |
  ForEach-Object {
    & $cc @targetFlags @defines @includes -c $_.FullName -o "$($_.BaseName).o"
  }
```

### Step 3: Link

```powershell
& $cc @targetFlags @defines -Wl,--entry=Reset_Handler -o "empty.out" *.o
```

## Common Errors and Fixes

| Error | Cause | Fix |
|-------|-------|-----|
| `DeviceFamily_MSPM0G3507 is undefined` | Missing `-D__MSPM0G3507__` | Add from `device.opt` |
| `__USE_SYSCONFIG__ is undefined` | Missing SysConfig define | Add `-D__USE_SYSCONFIG__` |
| `__STATIC_INLINE unknown type name` | Missing CMSIS include | Add `-I.../CMSIS/Core/Include` |
| `ti_msp_dl_config.h: No such file` | SysConfig not run or missing include path | Run SysConfig first, add `-I.../Debug` |
| `UART_BT_INST undefined` / `KEY_KEY1_PIN undefined` | Macro name mismatch between code and SysConfig | Regenerate SysConfig, verify macro names in generated `ti_msp_dl_config.h` |
| `HAL_GetTick undefined` | STM32 HAL function used on MSPM0 | Replace with `DL_SYSCTL_getTick()` |
| `ENC_LA_PORT undefined` | Code uses old separate-port macros | Replace with unified `ENC_PORT` (single GPIO group) |
| `unknown type name 'GPIO_PinState'` | STM32 HAL type on MSPM0 | Use `bool` + `DL_GPIO_readPins()` |
| `header file not found` for App/Bsp/Drv/Lib | Missing include paths | Add `-I` for each source directory |

## Critical Rules

### Rule 1: device.opt defines are mandatory

The file `Debug/device.opt` contains `-D__MSPM0G3507__` and `-D__USE_SYSCONFIG__`. These are NOT optional — DriverLib headers use conditional compilation based on `__MSPM0G3507__`. Always pass these as compiler defines.

### Rule 2: SysConfig output directory must be in include path

SysConfig generates `ti_msp_dl_config.h` into the output directory (typically `Debug/`). This path MUST be in the include list, or `#include "ti_msp_dl_config.h"` will fail.

### Rule 3: PowerShell array splatting for multi-word flags

Do NOT pass `-march=thumbv6m -mcpu=cortex-m0plus` as a single string. PowerShell treats the entire string as one argument. Use array syntax:

```powershell
# WRONG — single string, one argument
$flags = "-march=thumbv6m -mcpu=cortex-m0plus"
& $cc $flags ...

# CORRECT — array elements, separate arguments
$flags = @("-march=thumbv6m", "-mcpu=cortex-m0plus")
& $cc @flags ...
```

### Rule 4: STM32 HAL vs TI DriverLib API mapping

When migrating code from STM32 to MSPM0, these API replacements are needed:

| STM32 HAL | MSPM0 DriverLib |
|-----------|-----------------|
| `HAL_GetTick()` | `DL_SYSCTL_getTick()` |
| `HAL_GPIO_ReadPin(port, pin)` | `DL_GPIO_readPins(port, pin)` (returns bitmask, compare with `!= 0`) |
| `HAL_GPIO_WritePin(port, pin, state)` | `DL_GPIO_setPins()` / `DL_GPIO_clearPins()` |
| `GPIO_PIN_SET` / `GPIO_PIN_RESET` | `true` / `false` (or direct bitmask) |
| `HAL_UART_Transmit()` | `DL_UART_Main_fillTransmitFIFO()` or custom `Drv_UART_SendData()` |

### Rule 5: Verify macro names against generated headers

After SysConfig runs, always check `Debug/ti_msp_dl_config.h` for the actual macro names. The naming convention is:

- GPIO group: `{GROUP_NAME}_PORT`, `{GROUP_NAME}_{PIN_NAME}_PIN`, `{GROUP_NAME}_{PIN_NAME}_IOMUX`
- UART: `UART_{NAME}_INST`
- PWM: `PWM_{NAME}_INST`
- Timer: `TIMER_{NAME}_INST`

Pin `$name` in SysConfig determines the macro suffix. For example, if the pin name is `KEY1`, the macro is `KEY_KEY1_PIN` (not `KEY_KEY1_KEY1_PIN`).

## Quick Diagnostic Script

To check if all source files compile without errors:

```powershell
$cc = "E:\ti\ccs\ccs_base\compiler\ti-cgt-armclang_5.1.1.LTS\bin\tiarmclang.exe"
$sdk = "E:\ti\mspm0_sdk_2_10_00_04"
$projectRoot = "D:\Code\2025NUEDC\src\car\empty"

$defines = @("-D__MSPM0G3507__", "-D__USE_SYSCONFIG__")
$targetFlags = @("-march=thumbv6m", "-mcpu=cortex-m0plus", "-mfloat-abi=soft", "-mthumb", "-mlittle-endian", "-gdwarf-3", "-Wall", "-O2")
$includes = @(
    "-I$sdk\source",
    "-I$sdk\source\third_cmsis\CMSIS\Core\Include",
    "-I$projectRoot",
    "-I$projectRoot\Debug",
    "-I$projectRoot\App",
    "-I$projectRoot\Bsp",
    "-I$projectRoot\Drv",
    "-I$projectRoot\Lib"
)

$failCount = 0
Get-ChildItem -Recurse -Filter *.c -Path $projectRoot |
  Where-Object { $_.DirectoryName -notmatch "Release" } |
  ForEach-Object {
    $result = & $cc @targetFlags @defines @includes -c $_.FullName -o "$($_.BaseName).o" 2>&1
    if ($LASTEXITCODE -ne 0) {
      Write-Host "FAIL: $($_.Name)" -ForegroundColor Red
      Write-Host $result
      $failCount++
    } else {
      Write-Host "OK: $($_.Name)" -ForegroundColor Green
    }
  }
Write-Host "`nFailed: $failCount"
```
