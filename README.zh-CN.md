# muse-repo-explorer

[English](README.md) | [日本語](README.ja.md) | **简体中文** | [한국어](README.ko.md)

在 Muse（你的个人 AI 助手）的环境中保存 GitHub 仓库的本地克隆，从而：

- **Muse 从本地文件读取代码** —— 比通过连接器更快，消耗的 token 也少得多。
- **你在手机上阅读代码** —— 通过一个内嵌代码快照的私人"文件浏览器"页面（Muse 空间）。

## 快速开始：把这段内容粘贴给 Muse

复制下面整个代码块并发送给 Muse。过程中 Muse 只会问你两件事：
(1) GitHub 登录的一次性验证码，(2) 要克隆哪些仓库。

````text
请在我的环境中搭建 "muse-repo-explorer"（https://github.com/masato-umeno/muse-repo-explorer）。请严格遵守最后的隐私规则。

1. 安装工具（放在我的主目录下，以便在 VM 更换后仍然保留）
   - 从 github.com/x-motemen/ghq 下载最新版 ghq 二进制文件，放到 ~/.local/bin/ghq。
   - 从 github.com/cli/cli 下载最新版 gh（GitHub CLI）二进制文件，放到 ~/.local/bin/gh。
   - 分别用 --version 确认可以运行。

2. GitHub 登录（设备流程，仅 HTTPS）
   - 运行 `gh auth login --hostname github.com --git-protocol https --web`。
   - 把一次性验证码和 https://github.com/login/device 展示给我，等待我在浏览器中批准。
   - 完成后，报告 `gh auth status` 中的账户名，并运行 `gh auth setup-git`。
   - 不要使用 SSH。绝不要让我粘贴密码或 token。

3. 克隆我的仓库
   - 列出我可以访问的仓库（`gh repo list`，包括我所在的组织），先问我要克隆哪些，然后对每个运行 `ghq get <owner>/<repo>`。
   - 除非我要求，否则跳过已归档的仓库。

4. 安装快照工具
   - 运行 `ghq get https://github.com/masato-umeno/muse-repo-explorer`。
   - 将其 tools/ 目录中的所有文件复制到 ~/workspace/repo-explorer/（不要放在任何 git 仓库内），并为脚本添加执行权限。
   - 运行 `python3 ~/workspace/repo-explorer/update_snapshot.py`，确认生成了 snapshot.json。
   - 问我是否有不想在页面上显示的文件（例如 `.env*`、`*.pem`、`secrets/*`）。如果有，把这些 glob 写入 ~/workspace/repo-explorer/exclude.txt，然后重新运行 update_snapshot.py。

5. 安装 pull 钩子
   - 运行 `~/workspace/repo-explorer/install-hooks.sh`。
   - 在任意一个仓库执行 pull，确认 snapshot.json 已重新生成。

6. 创建浏览页面（Muse 空间）
   - 按照该仓库中 docs/explorer-page-spec.md 的规格创建。把 snapshot.json 作为单独的资源，使页面只需替换它即可更新。
   - 页面界面使用我的语言。
   - 保持页面私密，绝不要创建公开链接。

7. 更新
   - 当我说"更新浏览器页面"时：依次运行 update_snapshot.py 和 sync_status.py。仅当 sync_status.py 的退出码为 10 时，替换页面的快照资源，然后运行 `sync_status.py --mark`。
   - 可选：如果我已有定期任务（例如每周检查），可以把这个更新步骤附加到它的末尾，无需在聊天中报告。

8. 报告
   - `ghq list` 的结果、快照大小、创建的页面，以及失败的项目和原因。

隐私规则：
- 绝不要把 snapshot.json 纳入 git、放入公开仓库或上传到文件共享服务。
- 绝不要公开分享浏览页面。
- 绝不要在聊天、文件或日志中写入凭据（密码、token）。
- 只克隆我有合法访问权限的仓库。
````

## 开始之前 —— 三条规则

1. **快照就是你的全部源代码。** 不要把 `snapshot.json` 放进 git 或任何共享的地方。
2. **保持浏览页面私密。** 公开链接会让任何拿到链接的人读到你的代码。
3. **只用设备流程登录。** 绝不要把 GitHub 密码或 token 粘贴到聊天中。

详情：[docs/security.md](docs/security.md)（英文）

## 文档（英文）

| 文档 | 内容 |
| --- | --- |
| [How it works](docs/design.md) | 架构与设计决策 |
| [Security & privacy](docs/security.md) | 使用者规则，以及本公开仓库的安全检查 |
| [Manual setup](docs/manual-setup.md) | 不使用提示词的手动搭建（也适用于 Claude Code） |
| [Operations](docs/operations.md) | 更新、钩子、排除文件、卸载 |
| [Explorer page spec](docs/explorer-page-spec.md) | 快照格式与页面 UI 规格 |

## 参与贡献

本仓库是**公开**的。首次提交前请运行：

```sh
sh scripts/install-dev-hooks.sh
```

它会在提交前拦截快照、日志、token、私人邮箱地址，以及你在私人禁用词列表中写下的真实名称。
CI 也会在每次 push 时运行同样的检查。

## 许可证

MIT —— 参见 [LICENSE](LICENSE)。
