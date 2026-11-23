# muse-repo-viewer

[English](README.md) | [日本語](README.ja.md) | **简体中文** | [한국어](README.ko.md)

在 Muse 中运行的仓库查看器。它在 Muse 环境中保存 GitHub 仓库的本地克隆，从而：

- **你**可以在 Muse 的私有空间里用手机阅读和搜索代码，并就选中的行向 Muse 提问；
- **Muse** 从本地文件读取源代码，比通过连接器更快，消耗的 token 也更少。

介绍页面：<https://masato-umeno.github.io/muse-repo-viewer/>

## 搭建

复制下面这一行并粘贴到 Muse。Muse 会继续使用你平时的语言回复。

```text
Set up muse-repo-viewer for me by following https://github.com/masato-umeno/muse-repo-viewer/blob/main/MUSE_SETUP.md (keep replying in the language we normally use)
```

搭建过程中，你需要批准 GitHub 登录并选择要包含的仓库（可以用本仓库作为示例）。如果 Muse 在创建空间等步骤之前询问是否继续，请回复可以继续。以后要更新时，再次发送同一行即可。

## 使用方法

- **更新：** 请 Muse "更新查看器"。只上传有新提交的仓库。
- **添加仓库：** 请 Muse 克隆后再更新。
- **隐藏文件：** 在 `~/workspace/repo-viewer/exclude.txt` 中写入 `.env*` 等 glob 模式。
- **显示语言：** 可在页面设置（齿轮按钮）中更改。

## 安全

空间中包含所选仓库的全部源代码，请保持私有。搭建用的这一行会让 Muse 按照本仓库中的说明操作；如需固定版本，请把 URL 中的 `main` 换成提交 ID 或标签。详见[安全](docs/security.md)。

## 文档

文档以英文撰写。

| 文档 | 内容 |
| --- | --- |
| [架构](docs/architecture.md) | 组件、数据流、设计决策、token 效率 |
| [安全](docs/security.md) | 所处理的数据、内置保护机制、给使用者的建议 |
| [手动搭建](docs/manual-setup.md) | 不使用提示词，自行或通过 Claude Code 搭建的步骤 |
| [运维](docs/operations.md) | 更新、维护、故障排查、卸载 |
| [参考](docs/reference.md) | 命令、配置、状态文件、快照格式 |
| [查看器页面](docs/page.md) | 内置页面的交付形式与行为 |

## 参与贡献

本仓库为公开仓库。首次提交前请阅读 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 许可证

[MIT](LICENSE)
