---
name: paper-ingest
description: 把已选定的论文归档进项目文献库（papers 主题子目录 + 信息卡 + REFERENCE_INDEX + refs.bib 四处同步，借鉴思想必须登记来源）. Use when the user asks to 收录这篇论文/文献入库/登记引用/把 PDF 加进文献库. Do not use for 检索论文内容（用 paper-search）或写文献综述.
---

# Paper Ingest（文献入库）

把一篇**已选定**的论文归档进项目文献库，完成四处同步。项目规则：**禁止"用了不注明"**——凡借鉴思想/公式/设计/数据，或决策（ADR）、诊断中据以定案的文献解法，都必须可追溯。

## 步骤

1. **落文件**：PDF/提取文本放入 `traffic_rl_project/docs/papers/<主题子目录>/`，五个子目录按主题选（`01_coupler_physics` / `02_rl` / `03_formation` / `04_safety_mpc` / `05_energy_other`，清单见 `docs/papers/README.md`）。PDF 命名 `作者_短标题`，提取文本命名 `作者_短标题_提取文本.md`。归属拿不准时向用户确认，不要猜。
2. **信息卡**：在 `docs/papers/README.md` 登记条目（标题/作者/年份/venue/本地文件/一句话定位）。
3. **REFERENCE_INDEX.md**：新增一行——"技术/公式要点 → 来源（作者年份）→ 本地文件路径 / DOI"。**DOI 未核实到就只写 venue+年份，不编号**。
4. **refs.bib**：追加 BibTeX 条目，key 惯例 `作者小写年份_主题`（如 `rong2025_heavyhaul_dynamics`）。
5. **借鉴登记**：如果这篇论文支撑了某个设计/公式/对比方法/决策，在 REFERENCE_INDEX 该行写明"用在哪"（对应 ADR 编号或模块名）；纯背景阅读标注"背景"。
6. **验证**：Glob 确认文件真实落盘；Grep 确认四处（papers 目录、README 卡、INDEX、refs.bib）都已更新；DOI 能打开或标注未核实。

## 输出报告

入库完成后报告：文件路径、INDEX 行、bib key、借鉴登记内容；如有信息缺失（如查不到 DOI）明确列出，不替用户编造。
