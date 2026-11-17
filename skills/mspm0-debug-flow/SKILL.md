---
name: mspm0-debug-flow
description: MSPM0嵌入式项目三层调试流程技能。当用户需要调试小车或云台的硬件模块（电机、灰度传感器、编码器、陀螺仪、蓝牙等）时触发此技能。该技能提供从底层到应用层的渐进式调试方法论：Level 1 绕过应用层直接调用底层驱动、Level 2 解耦模块并输出调试信息、Level 3 使用完整应用层代码并增加调试输出。
---

# MSPM0 嵌入式三层调试流程

## 适用场景

调试 MSPM0G3507 嵌入式项目（小车/云台）中的硬件模块时，按以下三层渐进流程执行。每层通过后才进入下一层，确保问题定位清晰。

## 项目架构回顾

```
src/car/empty/          或 src/gimbal/empty/
├── Drv/                ← 最底层：GPIO/PWM/UART/I2C/Timer 驱动
├── Bsp/                ← 板级支持：motor_drv, encoder, grayscale, oled, bluetooth
├── App/                ← 应用逻辑：tracking, speed_ctrl, odometry, aiming_ctrl
├── Lib/                ← 共享库：pid, ringbuf, comm_protocol
└── empty.c             ← main() 入口
```

## 三层调试流程

### Level 1: 绕过应用层，直接调用底层

**目标**：验证硬件和底层驱动是否正常工作，排除硬件接线、GPIO配置、PWM参数等问题。

**原则**：
- `empty.c` 的 `main()` 中**只做 SYSCFG_DL_init + 直接调用 Drv/Bsp 层函数**
- **不调用任何 App 层函数**（不调 Tracking_Update、SpeedCtrl_Update 等）
- **不使用 HAL_GetTick()** — MSPM0 没有 STM32 HAL，使用 `BSP_GetTick()`（基于 SysTick 1ms 中断，见 `Bsp/bsp_init.c`）或 `delay_cycles()` 忙等
- 写 `empty.c` 时**必须包含 BSL 防护代码**（见 BSL 防护参考）

**具体步骤**：

1. 读取 `empty.c`，备份当前内容（存为注释块或单独文件）
2. 写 Level 1 测试代码：
   - BSL 防护 → `SYSCFG_DL_init()` → 底层模块 Init
   - 直接用 `DL_GPIO_setPins/clearPins`、`Drv_PWM_SetDuty`、`Drv_UART_SendData` 等底层 API
   - 用 `BSP_GetTick()` 或忙等做定时
3. Build + 烋录验证

**Level 1 通过标准**：底层硬件行为与预期一致（电机转/停、传感器读数正确、UART 有输出）。

**常见陷阱**：
- `DL_GPIO_initDigitalOutput()` **不包含 enableOutput**，必须紧跟 `DL_GPIO_enableOutput()`，否则 GPIO 输出驱动未开启，引脚始终 LOW
- SysConfig 生成的 `SYSCFG_DL_SYSTICK_init()` 配的是 1μs 周期，需要 `BSP_Init()` 重新配置为 1ms
- `DL_SYSCTL_getTick()` 函数**不存在**，TI MSPM0 SDK 没有此函数

### Level 2: 解耦模块，输出调试信息

**目标**：逐个验证 Bsp/App 层模块的封装逻辑是否正确，找出哪个模块有 bug。

**原则**：
- 在 `empty.c` 中**只初始化并调用需要调试的模块**，其他模块不 Init 不调用
- 每个被测试模块的关键中间变量**通过蓝牙/UART 输出**
- 用 `BSP_GetTick()` 做非阻塞定时

**具体步骤**：

1. 确定要调试的模块（如 MotorDrv、Tracking、SpeedCtrl）
2. 写 Level 2 测试代码：
   - BSL 防护 → `SYSCFG_DL_init()` → `BSP_Init()` → 只 Init 目标模块 → `Bluetooth_Init()`
   - 主循环中只调用目标模块的 Update 函数
   - 每 200-500ms 通过蓝牙输出：模块内部状态、中间计算结果、输入输出值
3. Build + 烋录验证

**Level 2 通过标准**：目标模块的输入→计算→输出链条完整正确，中间变量无异常。

**调试信息输出模板**：
```c
char buf[120];
snprintf(buf, sizeof(buf),
    "[模块名] 输入=%d 中间=%d 输出=%d 状态=%s\r\n",
    input_val, mid_val, output_val, status_str);
Bluetooth_SendString(buf);
```

### Level 3: 使用完整应用层代码，增加调试信息

**目标**：验证完整应用层逻辑（多模块级联）是否正常工作。

**原则**：
- `empty.c` 使用完整的正常流程：Init 所有模块 → 主循环调用所有 Update
- 在 App 层模块内部**增加调试输出**（不改变 empty.c 结构）
- 可以在模块的 Update 函数中加条件性调试输出（如每 N 次输出一次）

**具体步骤**：

1. 恢复 `empty.c` 为完整应用层版本
2. 在需要调试的 App 层模块（如 `speed_ctrl.c`、`tracking.c`）中：
   - 添加静态计数器，每 N 次调用输出一次调试信息
   - 输出：PID 输入/输出、偏差值、丢线状态、速度目标等
3. Build + 烋录验证

**Level 3 通过标准**：多模块级联工作正常，整个系统行为符合预期。

**在 App 层加调试输出的模式**：
```c
// 在模块内部加静态计数器
static uint32_t dbg_count = 0;

void Module_Update(void)
{
    // ... 正常逻辑 ...

    dbg_count++;
    if (dbg_count % 25 == 0) {  /* 每 25 次（约 500ms @ 50Hz）输出 */
        char buf[80];
        snprintf(buf, sizeof(buf),
            "[Module] key_var1=%d key_var2=%d\r\n",
            var1, var2);
        Bluetooth_SendString(buf);
    }
}
```

## BSL 防护代码（每个 empty.c 必须包含）

```c
/* BSL 防护 — 防止调试器意外进入 BSL 模式 */
DL_GPIO_initDigitalOutput(IOMUX_PINCM40);
DL_GPIO_clearPins(GPIOA, DL_GPIO_PIN_18);
DL_GPIO_enableOutput(GPIOA, DL_GPIO_PIN_18);
```

**注意**：这3行必须在 `SYSCFG_DL_init()` **之前**执行。

## tick 函数使用规范

| 函数 | 来源 | 单位 | 适用场景 |
|------|------|------|----------|
| `BSP_GetTick()` | `Bsp/bsp_init.c` | ms | 非阻塞定时（推荐） |
| `delay_cycles(n)` | TI DriverLib 内联 | CPU周期 | 精确忙等延时 |
| `DL_SYSCTL_getTick()` | **不存在** | — | **禁止使用** |
| `HAL_GetTick()` | STM32 HAL | — | **禁止使用** |

`BSP_GetTick()` 的使用：
```c
#include "Bsp/bsp_init.h"

uint32_t t0 = BSP_GetTick();
// ... do work ...
uint32_t elapsed = BSP_GetTick() - t0;  /* elapsed ms */
```

## GPIO 输出使能规范

每次调用 `DL_GPIO_initDigitalOutput()` 后，必须紧跟 `DL_GPIO_enableOutput()`：
```c
DL_GPIO_initDigitalOutput(MOTOR_DIR_B_MTR_AIN1_IOMUX);
DL_GPIO_enableOutput(MOTOR_DIR_B_PORT, MOTOR_DIR_B_MTR_AIN1_PIN);
```

SysConfig 的 `SYSCFG_DL_GPIO_init()` 已经做了 init + enable，但如果代码中再次调用 `initDigitalOutput()`（如 `MotorDrv_Init()`），会重置 OE 位，必须重新 enableOutput。

## PWM 参数规范

小车 PWM timer period = 200，duty 范围 0~200。`MOTOR_PWM_MAX = 200`。
- 速度环输出的目标速度值不能直接当 PWM 用
- Level 1 测试时 PWM 值应在 0~200 范围内
- 完整级联中：位置PID → 角度PID → 速度PID → PWM（逐级缩放）

## 流程决策图

```
硬件不工作？
  ├─ 是 → Level 1（直接底层驱动测试）
  │       ├─ 通过 → 进入 Level 2
  │       └─ 不通过 → 检查接线/SysConfig/GPIO enableOutput
  └─ 否（硬件OK但系统行为异常）
      ├─ 单模块有bug？ → Level 2（解耦单模块测试）
      │       ├─ 通过 → 进入 Level 3
      │       └─ 不通过 → 修该模块的封装逻辑
      └─ 多模块级联异常？ → Level 3（完整应用层 + 调试输出）
              ├─ 通过 → 调试完成
              └─ 不通过 → 回退 Level 2 定位具体模块
```
