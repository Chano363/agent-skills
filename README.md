# Agent Skills — 嵌入式开发与科研实践

本仓库收录我在本科期间（全国大学生电子设计竞赛、大创项目、嵌入式开发、多智能体强化学习科研）中，
借助 AI 编程 agent 逐步沉淀的自定义 skill。这些 skill 把反复踩过的坑、查过的文献、调过的参数、
被返工逼出来的写作纪律固化成可复用的工作流，让 agent 在同类任务上按我验证过的路径执行，
而不是每次从头摸索。

> 说明：本仓库只收录**本人围绕具体项目原创整理**的 skill。官方模板（skill-creator）、
> 第三方通用 skill（find-skills、grill-me、ui-update、doc-init 文档治理套件等）不计入。

## 收录清单

| Skill | 解决的问题 | 文件数 |
|---|---|---:|
| [`mspm0-ccs`](skills/mspm0-ccs/) | TI MSPM0 固件开发的工具中立 agent 规则，覆盖 CCS/Keil/CMake 三套工具链、SysConfig 校验、DriverLib API 与 9 个配套脚本 | 46 |
| [`mcu-debug`](skills/mcu-debug/) | 基于 MSPM0G3507 + AT8236/TB6612 真实踩坑记录的 MCU 外设调试技能，先硬件后软件的排查流程 | 3 |
| [`esp32-idf`](skills/esp32-idf/) | ESP32 ESP-IDF v5.4+ 固件开发规则，含环境搭建、sdkconfig 管理与 idf.py 构建烧录流程 | 4 |
| [`mspm0-debug-flow`](skills/mspm0-debug-flow/) | MSPM0 嵌入式三层渐进式调试流程（绕过应用层→模块解耦→完整应用），逐层定位硬件模块问题 | 2 |
| [`ccs-build`](skills/ccs-build/) | 用 tiarmclang 命令行编译 MSPM0G3507 固件的完整参数与工作流，脱离 CCS GUI | 1 |
| [`mspm0-sysconfig-generator`](skills/mspm0-sysconfig-generator/) | MSPM0G3507 SysConfig 文件生成规范，含引脚分配、外设冲突检查与模板 | 4 |
| [`debug-finder`](skills/debug-finder/) | C++/前端报错自动化调试技能：定位错误→修复→生成测试脚本→记录修复日志 | 5 |
| [`windows-disk-cleanup-scan`](skills/windows-disk-cleanup-scan/) | Windows 磁盘空间扫描与清理审核技能，只读扫描 + 三级风险分类（安全/需确认/需管理员） | 5 |
| [`defense-ppt`](skills/defense-ppt/) | 答辩/汇报 PPT 的大纲、文案与配图规范，源自中期答辩全过程复盘，含六条铁律（只改指定部分、数字须有归档背书、去黑话等） | 2 |
| [`discussion-doc`](skills/discussion-doc/) | 按读者身份（组员/导师/学长）分颗粒度的项目交流文档撰写技能，含现状核实与去黑话流程 | 2 |
| [`paper-search`](skills/paper-search/) | 论文检索与批判性阅读技能，先网络后本地，产出场景难点、前人缺陷与本方法可行性差距分析 | 1 |
| [`paper-ingest`](skills/paper-ingest/) | 论文入库技能，PDF/信息卡/REFERENCE_INDEX/refs.bib 四处同步，强制登记思想来源 | 1 |
| [`result-review`](skills/result-review/) | 训练/仿真实验结果审查与归档数据复图技能，含指标口径核对、跨组对比表与结论纪律 | 1 |
| [`venue-verify`](skills/venue-verify/) | 学术会议真实性与投稿窗口核实技能，只信一手，五步识别假会与截稿日期陷阱 | 1 |

共 **14 个 skill、78 个文件**。

## 按场景分类

**嵌入式开发效率**（让 agent 按项目真实工具链工作）
- `mspm0-ccs`、`ccs-build`、`mspm0-sysconfig-generator` — TI MSPM0 从 SysConfig 配置、命令行编译到 DriverLib API 的完整链路
- `esp32-idf` — ESP32 ESP-IDF 环境搭建与构建烧录

**硬件调试方法论**（把踩坑经验变成排查流程）
- `mcu-debug`、`mspm0-debug-flow` — 从物理连接、电源测量到外设驱动的渐进式定位，基于真实故障案例
- `debug-finder` — C++/前端报错的定位—修复—测试—日志闭环

**科研工作流**（重载列车多智能体强化学习项目，把返工教训固化成规则）
- `paper-search` / `paper-ingest` — 论文检索批判性阅读 + 入库四处同步，强制"用了不注明"零容忍
- `result-review` — 实验数据复用优先、指标口径核对（ADR 锚定）、结论纪律
- `venue-verify` — 投稿前只信一手，识别假会与"会期当截稿"陷阱
- `defense-ppt` — 答辩 PPT 的六条铁律：只改指定部分、数字有归档背书、藏拙、去黑话
- `discussion-doc` — 按读者身份（组员/导师/学长）控制颗粒度的对外文档

**工程与系统工具**
- `windows-disk-cleanup-scan` — 磁盘空间只读审计与三级风险分类

## 设计思路

每个 skill 遵循 Agent Skills 规范：`SKILL.md`（触发条件 + 工作流）+ `references/`（详细参考）
+ `scripts/`（可执行脚本）+ `assets/`（模板与片段）。核心原则：

1. **证据优先** — 参数、引脚、工具链路径来自真实项目代码，数字必须能在归档文件里指出来源；
2. **渐进定位** — 调试类 skill 强制按层推进，先在最底层复现问题，再往上叠加应用逻辑；
3. **只读先行** — 涉及系统操作的 skill 默认只读扫描，破坏性动作必须单独确认；
4. **返工驱动** — 科研写作类 skill 的每条规则都对应一次真实翻车，不写泛泛的最佳实践。

这些 skill 可在 Claude Code、OpenCode、Cursor、Codex 等支持 Agent Skills 的工具中加载使用。
