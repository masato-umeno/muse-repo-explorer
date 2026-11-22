# muse-repo-explorer

[English](README.md) | [日本語](README.ja.md) | **简体中文** | [한국어](README.ko.md)

muse-repo-explorer 在 Muse 环境中保存 GitHub 仓库的本地克隆，并提供以下两种用途：

- **面向 Muse：** 从本地文件读取源代码，比通过连接器更快，且显著减少 token 消耗。
- **面向使用者：** 基于克隆的快照生成私密的、面向手机浏览的代码浏览器（Muse 空间）。可以搜索文件名和文件内容，可以把选中的代码范围连同问题一起交给 Muse，Markdown 文件以排版后的形式显示，并渲染 Mermaid 图表。页面以使用者的语言（英文、日文、中文或韩文）显示，并可在设置中切换。每个仓库的内容仅在需要时加载，因此仓库数量增加时页面依然流畅。

## 搭建

将下面这一行发送给 Muse（保持英文即可）：

```text
Set up muse-repo-explorer for me by following https://github.com/masato-umeno/muse-repo-explorer/blob/main/MUSE_SETUP.md
```

Muse 会读取 [MUSE_SETUP.md](MUSE_SETUP.md)，之后由工具本身逐步引导。过程中需要你批准 GitHub 登录并选择要包含的仓库。至少需要一个仓库，也可以使用本仓库作为示例。页面将以你平时与 Muse 交流所用的语言显示，并且可以随时在页面的设置（齿轮按钮）中更改。之后可以随时再次发送同一行：已完成的步骤会被跳过，现有环境（包括用旧版本搭建的环境）会更新到最新版本。

这一行会让 Muse 遵循存放在本仓库中的指示。如需固定版本，请将网址中的 `main` 替换为提交 ID 或发布标签。

## 使用方法

- **更新页面：** 请 Muse "更新浏览器页面"，或再次发送搭建用的那一行。只有在仓库有新提交时才会更新空间，并且只上传相应仓库的文件。
- **添加仓库：** 请 Muse 克隆相应仓库，然后执行更新。
- **隐藏文件：** 在 `~/workspace/repo-explorer/exclude.txt` 中写入 glob 模式（例如 `.env*`、`*.pem`）。详见[运维](docs/operations.md)。

## 安全

快照包含所有已包含仓库的完整源代码。请保持浏览器页面私密，不要提交或共享 `snapshot.json`，并且只通过设备流程登录。完整说明请参见[安全](docs/security.md)。

## 文档

文档以英文撰写。

| 文档 | 内容 |
| --- | --- |
| [架构](docs/architecture.md) | 组件、数据流、设计决策、token 效率 |
| [安全](docs/security.md) | 所处理的数据、内置保护机制、给使用者的建议 |
| [手动搭建](docs/manual-setup.md) | 不使用提示词，自行或通过 Claude Code 搭建的步骤 |
| [运维](docs/operations.md) | 更新、维护、故障排查、卸载 |
| [参考](docs/reference.md) | 命令、配置、状态文件、快照格式 |
| [浏览器页面](docs/page.md) | 内置页面的交付形式与行为 |

## 参与贡献

本仓库为公开仓库。首次提交前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证

[MIT](LICENSE)
