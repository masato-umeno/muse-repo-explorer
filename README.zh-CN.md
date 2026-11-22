# muse-repo-explorer

[English](README.md) | [日本語](README.ja.md) | **简体中文** | [한국어](README.ko.md)

muse-repo-explorer 在 Muse 环境中保存 GitHub 仓库的本地克隆，并提供以下两种用途：

- **面向 Muse：** 从本地文件读取源代码，比通过连接器更快，且显著减少 token 消耗。
- **面向使用者：** 基于克隆的快照生成私密的、面向手机浏览的代码浏览器（Muse 空间）。支持英文、日文、中文和韩文，并提供浅色与深色主题。

## 搭建

将以下提示词发送给 Muse。搭建过程中需要你完成两项操作：批准 GitHub 登录，以及选择要包含的仓库。提示词可以随时重新发送，已完成的步骤会被跳过。

````text
请在我的环境中搭建 "muse-repo-explorer"，全程遵守以下规则：
- 节省 token：只运行下面列出的命令，只阅读它们的简短输出。不要打开、打印或粘贴 snapshot.json、index.html 或 explorer.html，而是按文件路径直接上传。不要自己编写脚本或自己制作页面，页面已经做好了。
- 隐私：保持页面私密，绝不创建公开链接。绝不向我索要密码或 token。只克隆我选择的仓库。

在以下步骤中，C 指的是：python3 ~/workspace/muse-repo-explorer/tools/repo_explorer.py

1. 获取工具。如果 ~/workspace/muse-repo-explorer 已存在，运行 `git -C ~/workspace/muse-repo-explorer pull --ff-only`；否则运行 `git clone https://github.com/masato-umeno/muse-repo-explorer ~/workspace/muse-repo-explorer`。然后运行 `C setup`。
2. 登录（如果 setup 输出了 "signed in" 则跳过）。运行 `C login`，把输出的网址和验证码原样展示给我。然后运行 `C login --wait`，我批准后它就会结束。
3. 选择仓库。运行 `C list` 并把结果给我看，问我要包含哪些（我可能会回答"所有私有仓库"之类）。按我的选择运行 `C clone owner/repo ...`。
4. 构建。运行 `C refresh`。
5. 创建页面。把 refresh 输出的文件原样上传，创建一个名为"仓库浏览器"的私密 Muse 空间：优先使用 index.html 和 snapshot.json 两个文件；如果空间只能放一个 HTML 文件，就改用 explorer.html。然后运行 `C mark-synced --mode two-file`（单文件则用 `--mode single-file`）。
6. 用不超过 3 行向我报告：GitHub 账户、仓库数量、创建的页面。

请记住以后的做法：当我说"更新浏览器页面"时，或在我已有的定期任务末尾，运行 `C refresh`。如果输出 UP_TO_DATE，就到此为止。如果输出 PAGE_UPDATE_NEEDED，只在页面中替换它指出的文件，然后运行 `C mark-synced`。
````

## 使用方法

- **更新页面：** 请 Muse "更新浏览器页面"。只有在仓库有新提交时才会更新页面，并且只替换数据文件。
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
