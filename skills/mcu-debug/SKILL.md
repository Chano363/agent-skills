---
name: mcu-debug
description: MCU 外设驱动/硬件调试技能，基于 MSPM0G3507 + AT8236/TB6612 项目的真实踩坑记录。适用于：上电飞车、单片机重启、I2C/UART 不工作、PWM 异常、编码器信号异常等外设级问题排查。当用户描述硬件异常现象时优先触发此技能。
---

# MCU 外设调试

## 核心原则

遇到异常现象时，**先检查硬件，再怀疑软件**。反复查代码浪费的时间往往比查硬件更多。

## 排查流程

### 第一步：物理连接检查
- 排线是否插反（尤其注意母座 1 脚标记，无标记时用万用表量通断确认）
- 排线是否完全插入并锁紧

### 第二步：电源测量
- 编码器 VCC 必须 3.3V（5V 会导致信号尖峰使 MCU 重启）
- 各电源轨电压正常

### 第三步：关键信号测量
- 示波器量 PWM 引脚、方向引脚实际电平
- 原理图中检查 I2C/UART 引脚是否被特殊功能占用（BLS、BOOT 等）

### 第四步：隔离排查
- 拔掉非必要外设缩小范围
- 杜邦线 vs PCB 对比实验

## 常见驱动故障

### AT8236 上电飞车
排线插反错位信号 → 驱动输入异常 → 全速旋转。**不是软件问题。**

### TB6612 驱动
需要 IN1=H, IN2=L **同时** PWM 有效才转，初始化时 GPIO 默认 LOW 可安全避免飞车。

### 编码器异常
- VCC 必须 3.3V
- PCB 走线寄生参数可能导致过冲（杜邦线可正常但 PCB 不行）

### I2C 引脚冲突
MSPM0G3507 某些引脚复用 BLS（bootloader）功能，分配到此引脚的 I2C 无法工作。

## 参考文件
- `references/debugging-checklist.md` — 症状→原因映射表与排查顺序
- `references/debugging-cases.md` — 项目真实踩坑完整记录

## 寄存器验证
当驱动层行为可疑时，绕过抽象层直接读寄存器：
```c
uint16_t cc = DL_TimerA_getCaptureCompareValue(inst, DL_TIMER_CC_0_INDEX);
bool running = DL_TimerA_isRunning(inst);
```
