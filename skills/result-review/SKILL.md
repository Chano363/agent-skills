---
name: result-review
description: 审查训练/仿真实验结果并复用归档数据复图（选对归档目录、指标口径核对、跨组对比表、按生图规范重画）. Use when the user asks 看训练结果/整理实验数据/对比几个实验/重画图表/改图样式. Do not use for 启动训练或修改训练代码.
---

# Result Review（实验结果审查与复图）

审查实验结果 + 从已归档数据复图。铁律：**数据与绘图分离——默认复用归档数据重画，不重跑仿真**；只有数据确实缺失才允许重算，且必须补存归档供下次复用。

## 步骤

1. **选对归档目录**：候选在 `traffic_rl_project/outputs/` 下（results / sim_validation/phys_validation/<语义前缀_时间戳> / sim_validation/figures/<主题>）。**不可只看名字最新**——读目录内 metadata（config、seed、时间戳、实验名）确认装的是用户要的那次实验；选错 = 结论全错。
2. **指标口径核对**：车钩力一律用**每车钩断面力（kN）**口径（`coupler_interface_forces()`，ADR-018）；安全线 1000 kN，验收档位按 ADR-036（正常运行 ≤1000 / 制动工况验收 ≤1500 / 硬顶 2250）。速度 km/h、行程 km。口径对不上别人的图 = 不可比，先声明口径再比。
3. **对比表**：同口径跨组对比（组别按实验矩阵：D-Rule / 单列 RL 范式行 / Formation-MPC / D-RL / 消融列），标注 seed 数与统计量（均值±标准差）；单 seed 结果必须标注"单 seed，不作结论"。
4. **复图**（遵循 `docs/rules/EXECUTION_RULES.md` 生图规范）：
   - 图落**策展目录** `outputs/sim_validation/figures/<主题>/`（允许覆盖）；原始数据留**时间戳归档**（不覆盖）；禁止为改样式另建归档
   - 图内文字一律英文（标题/轴/图例/colorbar）；轴标签 = 物理量 + 单位（如 `Coupler force (kN)`）；标题用陈述式短语，禁 `vs`、箭头串、中英混排
   - 车钩力图必须画 1000 kN 安全线；状态量给语义标注（如 `Air brake state (1 = applied)`）
5. **结论纪律**：协同增益类 claim 只落**消融列**对比（同算法、有无编队上下文），基线行不承载 claim；安全叙事不归功于 RL 本身；超出数据支撑的结论（单 seed 外推、未跑的工况）一律不写。

## 输出报告

列：用了哪个归档（含 metadata 摘要）、指标口径、对比表、生成的图路径；如发现归档缺数据/口径不一致，明确指出并给补存建议。
