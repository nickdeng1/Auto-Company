# Windows + WSL Setup Guide

本项目在 Windows 上采用：

- Windows PowerShell 作为控制入口
- WSL2 (Ubuntu + systemd) 作为执行内核
- WSL `systemd --user` 提供守护与崩溃自拉起
- Windows `scripts/windows/awake-guardian-win.ps1` 提供运行时防睡眠

## 1. 一次性安装（WSL 内）

在 Ubuntu 终端执行：

```bash
sudo apt update
sudo apt install -y make jq curl

# 安装 Node.js（推荐 LTS）
curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
sudo apt install -y nodejs

# 安装 Codex CLI
npm install -g @openai/codex
```

## 2. 一次性自检（WSL 内）

```bash
make --version
codex --version
jq --version
systemctl --user --version
ps -p 1 -o comm=
```

判定标准：
- `systemctl --user --version` 成功
- `ps -p 1 -o comm=` 输出 `systemd`

建议额外检查 Codex 路径：

```bash
bash -lc 'command -v codex; codex --version'
bash -ic 'command -v codex; codex --version'
```

应优先命中 WSL 本地路径（`/home/<user>/...`），避免 `/mnt/c/...`。

## 3. 前置事项（每次开始前）

1. 只在 `clone_win/` 运行与提交，`clone/` 仅留档。
2. WSL 内 `make`、`codex`、`jq`、`systemctl --user` 可用。
3. `codex` 在 WSL 内已登录且可用。
4. 建议确认 `codex` 路径优先是 WSL 本地路径（`/home/...`）。

可选快速检查（PowerShell）：

```powershell
wsl -d Ubuntu bash -lc 'make --version; codex --version; jq --version; systemctl --user --version'
wsl -d Ubuntu bash -lc 'command -v codex'
```

## 4. 推荐操作（标准）

在 `clone_win` 目录运行：

```powershell
.\scripts\windows\start-win.ps1 -CycleTimeoutSeconds 1800 -LoopInterval 30
.\scripts\windows\status-win.ps1
.\scripts\windows\monitor-win.ps1
.\scripts\windows\last-win.ps1
.\scripts\windows\cycles-win.ps1
.\scripts\windows\stop-win.ps1
```

说明：
- `.\scripts\windows\start-win.ps1` 会写入 `.auto-loop.env`，并启动 `auto-company.service` + `awake guardian`
- `.\scripts\windows\stop-win.ps1` 会停止 `auto-company.service` 并关闭 `awake guardian`

推荐参数：
- `CycleTimeoutSeconds`：`900-1800`
- `LoopInterval`：`30-60`

