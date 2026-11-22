# muse-repo-explorer

[English](README.md) | [日本語](README.ja.md) | **简体中文** | [한국어](README.ko.md)

在手机上阅读你的 GitHub 代码，同时让 Muse（你的个人 AI 助手）以很低的成本读取代码。

- **Muse 从本地克隆读取代码**：比通过连接器更快，消耗的 token 也少得多。
- **你在手机上浏览代码**：通过私人的浏览器页面（Muse 空间）。页面已内置在本仓库中，
  支持 English / 日本語 / 中文 / 한국어，并支持浅色和深色主题。

## 快速开始：把这段内容粘贴给 Muse

复制下面整个代码块并发送给 Muse。你只需要做两件事：
批准 GitHub 登录验证码，以及选择要包含的仓库。

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

以后再次粘贴也没问题：已完成的步骤会自动跳过。

## 开始之前：三条规则

1. **快照就是你的全部源代码。** 不要把 `snapshot.json` 放进 git 或任何共享的地方。
2. **保持浏览页面私密。** 公开链接会让任何拿到链接的人读到你的代码。
3. **只用设备流程登录。** 绝不要把 GitHub 密码或 token 粘贴到聊天中。

详情：[docs/security.md](docs/security.md)（英文）

## 文档（英文）

| 文档 | 内容 |
| --- | --- |
| [How it works](docs/design.md) | 架构、设计决策、如何节省 token |
| [Security & privacy](docs/security.md) | 使用者规则，以及本公开仓库的安全检查 |
| [Manual setup](docs/manual-setup.md) | 手动搭建（也适用于 Claude Code）与命令参考 |
| [Operations](docs/operations.md) | 更新、钩子、排除文件、卸载 |
| [Explorer page spec](docs/explorer-page-spec.md) | 快照格式与内置页面 |

## 参与贡献

本仓库是**公开**的。首次提交前请运行：

```sh
sh scripts/install-dev-hooks.sh
```

它会在提交前拦截快照、日志、token、私人邮箱地址，以及你在私人禁用词列表中写下的真实名称。
CI 也会在每次 push 时运行同样的检查。

## 许可证

MIT，参见 [LICENSE](LICENSE)。
