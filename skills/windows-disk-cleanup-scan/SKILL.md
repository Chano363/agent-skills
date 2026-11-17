---
name: windows-disk-cleanup-scan
description: Scan Windows drives for disk-space consumers and classify cleanup candidates into (1) safe caches/temp, (2) user data that needs confirmation, and (3) admin-only items. Use when the user asks to 扫描磁盘/看看C盘D盘哪些可以清理/磁盘空间去哪了, or asks for a disk cleanup audit, large-file report, or "what is taking up space" on Windows.
---

# Windows Disk Cleanup Scan

扫描 Windows 磁盘、定位空间占用、给出可执行的清理清单。**只读扫描，不删除**；删除必须单独获得用户确认。

## 工作流

1. **磁盘概览**（秒级）：列出各盘容量/剩余，判断紧张程度。
2. **启动全盘扫描**（慢，放后台）：每个盘一个 `scan-drive.ps1` 进程，一次遍历同时得到顶层目录大小、根目录大文件、全盘 >300MB 大文件。
3. **测常见清理点**（较快）：`measure-targets.ps1` 输出缓存/临时/回收站等标准位置的大小。
4. **下钻**：对占用最大的 2–3 个目录用 `measure-paths.ps1 -Children` 拆解。
5. **分类报告**：安全 / 需确认 / 需管理员，并给出预计可释放空间。

## 命令

```powershell
# 1) 概览
Get-CimInstance Win32_LogicalDisk -Filter "DriveType=3" |
  Select-Object DeviceID, @{n='TotalGB';e={[math]::Round($_.Size/1GB,1)}},
                @{n='FreeGB';e={[math]::Round($_.FreeSpace/1GB,1)}}

# 2) 全盘扫描（每个盘一个后台任务；-OutFile 用绝对路径）
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\scan-drive.ps1 `
  -Root 'C:\' -OutFile "$PWD\c-scan.json" -LargeThresholdMB 300
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\scan-drive.ps1 `
  -Root 'D:\' -OutFile "$PWD\d-scan.json" -LargeThresholdMB 300

# 3) 标准清理点
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\measure-targets.ps1

# 4) 下钻
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\measure-paths.ps1 `
  -Paths 'C:\Users\me\AppData\Local' -Children

# 5) 读结果（JSON 为 UTF-8，PS 5.1 必须指定编码）
Get-Content .\c-scan.json -Raw -Encoding UTF8 | ConvertFrom-Json
```

## 判读规则

- **顶层目录大小**看 `topDirs`；**单个巨型文件**看 `largeFiles`；根目录的 `pagefile.sys / hiberfil.sys / swapfile.sys` 在 `rootFiles`。
- **扫描总量 > 系统显示已用**是正常的：WinSxS 硬链接被重复计数；系统还原点（VSS）是隐藏的，非管理员扫不到。差 30–50 GB 很常见，报告里要说明。
- 报告为 **0 GB 但确实存在**的目录（`C:\Windows\Temp`、`$Recycle.Bin`、`WindowsApps`、`ProgramData`、`Program Files`）通常是 **ACL 拒绝访问**，不是空目录。非管理员扫描时不要下"为空"的结论。
- 中文路径在 JSON 里正常；但 **PowerShell 5.1 会把无 BOM 的 UTF-8 脚本按 ANSI 解析**，脚本里写中文会导致语法错误——脚本一律保持纯 ASCII，输出用 `Set-Content -Encoding UTF8`。

## 分类标准

| 类别 | 判据 | 例子 |
|---|---|---|
| ✅ 安全 | 缓存/临时/索引/日志，删除后自动重建，不丢用户内容 | uv/npm/pip 缓存、Temp、DXCache、vscode-cpptools ipch、JetBrains caches、Arduino staging |
| ⚠️ 需确认 | 应用数据，可能含聊天记录、草稿、模型、配置 | Tencent/WeChat、WPS、剪映草稿、IDE 工作区、浏览器 Profile |
| 🔧 需管理员 | 系统组件、更新缓存、还原点、受保护目录 | WinSxS(DISM)、`$WinREAgent`、SoftwareDistribution、VSS |
| 📦 数据 | 用户文件/项目/数据集 | 文档、代码、游戏、视频素材 → 建议迁移到空闲盘而非删除 |

## 常见大头（按经验）

- 开发缓存：`npm-cache`、`uv\cache`、`pip\cache`、`ms-playwright`、`.gradle`、`.m2`、conda `pkgs`（`conda clean -p -t`）。
- IDE 索引：`vscode-cpptools\ipch`、JetBrains `caches`、`.lingma`、TRAE/Qoder 的 `database.db`。
- 显卡着色器：`%LOCALAPPDATA%\NVIDIA\DXCache|GLCache`。
- 聊天软件：`Documents\Tencent Files`、`Documents\WeChat`、`AppData\Roaming\Tencent`。
- 安装包残留：`Arduino15\staging`、`$WinREAgent`、`Windows\Installer`（**不要手删**）、各类 `*Updater\*.exe`。
- 重复文件：同一安装包散落在多个 agent 工作区/下载目录时，保留一份即可。

## 报告格式

1. 磁盘现状表（总容量/剩余/已用%）。
2. 每个盘一张表：项目 | 大小 | 位置 | 建议（附清理命令）。
3. 明确区分"可放心清"与"需确认"，给出合计可释放空间。
4. 结尾询问是否执行，**不要自行删除任何东西**。

## 性能参考

单遍扫描（.NET 枚举，跳过 reparse point）在本机实测：C: 202 GB ≈ 17 min，D: 275 GB ≈ 64 min（文件数多、杀软实时扫描会显著拖慢）。全盘扫描务必后台跑，期间先做常见清理点测量。
