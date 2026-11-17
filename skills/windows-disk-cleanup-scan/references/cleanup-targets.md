# 常见可清理位置速查

按"安全等级"排列。**安全 = 删了会自动重建、不丢用户内容**；执行前确认对应程序已关闭。

## ✅ 安全（缓存 / 临时 / 索引）

| 位置 | 典型大小 | 清理方式 |
|---|---|---|
| `%LOCALAPPDATA%\Temp`、`C:\Windows\Temp` | 1–10 GB | 直接清空内容（占用中的文件会跳过） |
| `%LOCALAPPDATA%\npm-cache` | 1–10 GB | `npm cache clean --force` |
| `%LOCALAPPDATA%\uv\cache` | 1–10 GB | `uv cache clean` |
| `%LOCALAPPDATA%\pip\cache` | 0.1–2 GB | `pip cache purge` |
| `%LOCALAPPDATA%\NuGet\v3-cache` | 0.1–2 GB | `dotnet nuget locals all --clear` |
| `%LOCALAPPDATA%\Microsoft\vscode-cpptools` | 1–8 GB | 关闭 VS Code 后删除（ipch / BROWSE.VC.DB） |
| `%LOCALAPPDATA%\JetBrains\*\caches` `\log` | 0.5–5 GB | 关闭 IDE 后删除 caches/log |
| `%LOCALAPPDATA%\NVIDIA\DXCache`、`GLCache` | 1–8 GB | 删除内容，游戏会重建着色器缓存 |
| `%LOCALAPPDATA%\D3DSCache` | 0–1 GB | 删除 |
| 浏览器 `...\User Data\Default\Cache` | 0.2–2 GB | 浏览器内清缓存最稳 |
| `%LOCALAPPDATA%\Arduino15\staging` | 0.5–3 GB | 只删 staging，不要删 packages |
| `%LOCALAPPDATA%\CrashDumps`、`%LOCALAPPDATA%\Microsoft\Windows\WER` | 0–2 GB | 删除 |
| `C:\$WinREAgent` | 0.5–3 GB | 管理员删除，更新残留 |
| `C:\Windows\SoftwareDistribution\Download` | 0–10 GB | 停 wuauserv 后清空，或 `cleanmgr` |
| 回收站 | 0–50 GB | `Clear-RecycleBin -Force` |

## ⚠️ 需确认（应用数据，可能含个人内容）

| 位置 | 说明 |
|---|---|
| `%APPDATA%\Tencent`、`Documents\Tencent Files`、`Documents\WeChat` / `xwechat_files` | QQ/微信聊天记录与文件，优先用软件内"存储空间管理" |
| `%APPDATA%\kingsoft`、`Documents\WPS Cloud Files` | WPS 云缓存/备份 |
| `%LOCALAPPDATA%\JianyingPro`、`JianyingPro Drafts` | 剪映缓存、模型、草稿 |
| `%APPDATA%\Code`、`%APPDATA%\Trae*`、`%LOCALAPPDATA%\Programs` | IDE 扩展、工作区、AI 会话数据库 |
| `%LOCALAPPDATA%\ms-playwright` | 不跑前端自动化测试才可删 |
| `.workbuddy` / `.lingma` / `.codex` 等 agent 目录 | 会话附件与索引，确认无引用后再删 |
| `%LOCALAPPDATA%\Packages` | UWP 应用数据，删单个应用的数据即可 |

## 🔧 需管理员（收益大、风险中）

```powershell
# 组件存储清理（可释放数 GB；/ResetBase 后无法卸载旧更新）
Dism /Online /Cleanup-Image /AnalyzeComponentStore
Dism /Online /Cleanup-Image /StartComponentCleanup /ResetBase

# 更新缓存 / 系统文件
cleanmgr /sageset:1     # 勾选后
cleanmgr /sagerun:1

# 还原点（System Restore 默认占 15% 磁盘）
vssadmin list shadowstorage
vssadmin delete shadows /for=C: /oldest
```

**永远不要手动删**：`C:\Windows\Installer`（卸载/修复要用，用 PatchCleaner 处理孤立项）、`C:\Windows\WinSxS`、`C:\Windows\System32`、`C:\Program Files\WindowsApps`。

## 📦 数据搬迁（不是删除）

项目、数据集、视频素材、游戏 → 移到空闲盘。常见冗余：数据集压缩包与解压后的目录并存、同一安装包散落在多个工作区。先用大小 + 文件名比对，确认解压完整再删压缩包。
