# MSPM0 调试常见陷阱参考

## 1. GPIO 输出使能 (OE) 问题

**症状**：方向引脚/控制引脚始终 LOW，`DL_GPIO_setPins()` 写了 DOUT 但物理引脚不输出。

**根因**：`DL_GPIO_initDigitalOutput()` 只配置 pinmux，**不清除也不设置 DOE 位**。但如果代码中再次调用 `initDigitalOutput()`，某些 SDK 版本可能重置 OE。

**解决**：每次 `DL_GPIO_initDigitalOutput()` 后紧跟 `DL_GPIO_enableOutput()`：
```c
DL_GPIO_initDigitalOutput(PINCM_XXX);
DL_GPIO_enableOutput(PORT, PIN);
```

SysConfig 生成的 `SYSCFG_DL_GPIO_init()` 已包含 enableOutput，但 `MotorDrv_Init()` 等重新调用 `initDigitalOutput` 的函数需要自己补 enableOutput。

## 2. HAL_GetTick / DL_SYSCTL_getTick 不存在

**症状**：链接报 `undefined symbol`。

**根因**：
- `HAL_GetTick()` 是 STM32 HAL 库函数，TI MSPM0 项目没有
- `DL_SYSCTL_getTick()` 在 MSPM0 DriverLib 中**不存在**（某些其他 TI 系列可能有）

**解决**：使用 `BSP_GetTick()`（基于 SysTick 1ms 中断，见 `Bsp/bsp_init.c`）。

## 3. SysTick 周期配置错误

**症状**：定时逻辑完全失效，`BSP_GetTick()` 返回值飞了或不变。

**根因**：SysConfig 默认配 `DL_SYSTICK_init(32)` = 32 ticks @ 32MHz = 1μs 周期，不是 1ms。

**解决**：在 `BSP_Init()` 中重新配置：
```c
DL_SYSTICK_disable();
DL_SYSTICK_init(32000);       /* 32MHz / 32000 = 1ms */
DL_SYSTICK_enableInterrupt();
DL_SYSTICK_enable();
```

## 4. PWM 值超出 timer period

**症状**：电机速度不符合预期，PWM 被 截断。

**根因**：timer period = 200，duty 范围 0~200。但 SpeedCtrl 的 `base_speed=500`、`corner_speed=300` 是级联中间值，直接当 PWM 就被 截断到 200。

**解决**：
- Level 1 测试：PWM 值在 0~200 范围
- 完整级联：速度PID 输出才是 PWM 值，base_speed 是速度目标

## 5. BSL 防护缺失

**症状**：调试器连接后芯片进入 BSL（Bootloader）模式，无法正常运行。

**根因**：PA18 (PINCM40) 在上电时若为高电平，MSPM0 会进入 BSL。

**解决**：在 `main()` 最开头、`SYSCFG_DL_init()` 之前：
```c
DL_GPIO_initDigitalOutput(IOMUX_PINCM40);
DL_GPIO_clearPins(GPIOA, DL_GPIO_PIN_18);
DL_GPIO_enableOutput(GPIOA, DL_GPIO_PIN_18);
```

## 6. car_app.h 已删除

**症状**：编译报 `file not found: car_app.h`。

**根因**：`car_app.c/h` 已从项目中删除（被拆分为 tracking、speed_ctrl、odometry 等独立模块），但 `bluetooth_cmd.c` 仍引用它。

**解决**：`bluetooth_cmd.c` 移除 `#include "../App/car_app.h"`，命令处理改为回显。

## 7. bool 类型未声明

**症状**：编译报 `unknown type name 'bool'`。

**根因**：C99 的 `bool` 需要 `#include <stdbool.h>`。

**解决**：在头文件中加 `#include <stdbool.h>`。

## 8. 备份 .c 文件被 Keil 编译

**症状**：链接报 `symbol "main" redefined`。

**根因**：Keil 编译所有 `.c` 文件，备份文件也有 `main()`。

**解决**：备份文件改扩展名为 `.c.bak` 或 `.bak`，Keil 不编译。
