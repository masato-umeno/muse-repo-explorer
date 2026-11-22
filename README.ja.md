# muse-repo-explorer

[English](README.md) | **日本語** | [简体中文](README.zh-CN.md) | [한국어](README.ko.md)

GitHub のコードをスマホで読めるようにし、Muse（パーソナルAIエージェント）にも低コストで読ませる仕組みです。

- **Muse はローカル clone からコードを読む**：コネクタ経由より速く、トークン消費もずっと少ない。
- **あなたはスマホでコードを読む**：自分専用のエクスプローラーページ（Muse のスペース）で。ページは同梱済みで、
  English / 日本語 / 中文 / 한국어、ライト／ダーク両対応です。

## はじめかた：これを Muse に貼るだけ

下のブロックを丸ごとコピーして Muse に送ってください。あなたがやることは、
GitHub ログインコードの承認と、対象リポジトリの選択の2つだけです。

````text
「muse-repo-explorer」を私の環境に構築してください。作業中は常に次のルールを守ってください。
- トークン節約：下に書いたコマンドだけを実行し、その短い出力だけを読むこと。snapshot.json・index.html・explorer.html は開かず、表示も貼り付けもせず、ファイルパスのままアップロードすること。独自のスクリプトを書いたりページを自作したりしないこと（ページは完成品があります）。
- プライバシー：ページは非公開のままにし、公開リンクは作らないこと。パスワードやトークンを私に求めないこと。clone するのは私が選んだリポジトリだけにすること。

以下の手順で C は次のコマンドを指します：python3 ~/workspace/muse-repo-explorer/tools/repo_explorer.py

1. ツールの取得。~/workspace/muse-repo-explorer があれば `git -C ~/workspace/muse-repo-explorer pull --ff-only`、なければ `git clone https://github.com/masato-umeno/muse-repo-explorer ~/workspace/muse-repo-explorer` を実行する。続けて `C setup` を実行する。
2. サインイン（setup が "signed in" と表示したら省略）。`C login` を実行し、表示された URL とコードをそのまま私に見せる。続けて `C login --wait` を実行する（私が承認すると終わる）。
3. リポジトリの選択。`C list` を実行して結果を私に見せ、どれを含めるか聞く（「プライベートのもの全部」のように答えることがあります）。私の選んだものを `C clone owner/repo ...` で取得する。
4. ビルド。`C refresh` を実行する。
5. ページの作成。refresh が表示したファイルを、手を加えずにアップロードして、非公開の Muse スペース「リポジトリエクスプローラー」を作る。できれば index.html と snapshot.json の2ファイル構成にし、スペースが HTML 1ファイルしか持てない場合は explorer.html を使う。その後 `C mark-synced --mode two-file`（1ファイルの場合は `--mode single-file`）を実行する。
6. 3行以内で報告：GitHub アカウント、リポジトリ数、作成したページ。

今後のために覚えておいてください：私が「エクスプローラーを最新化して」と言ったとき、または既存の定期ジョブの最後に、`C refresh` を実行する。UP_TO_DATE と出たらそこで終了。PAGE_UPDATE_NEEDED と出たら、指示されたファイルだけをページで差し替え、`C mark-synced` を実行する。
````

あとでもう一度貼っても大丈夫です。済んでいる手順はスキップされます。

## 始める前に：3つのルール

1. **スナップショットはソースコードそのもの。** `snapshot.json` を git にも共有先にも置かない。
2. **閲覧ページは非公開のまま。** 公開リンクを作ると、リンクを知る誰でもコードを読めてしまう。
3. **ログインはデバイスフローだけ。** GitHub のパスワードやトークンをチャットに貼らない。

詳しくは [docs/security.md](docs/security.md)（英語）

## ドキュメント（英語）

| ドキュメント | 内容 |
| --- | --- |
| [How it works](docs/design.md) | 全体像、設計判断、トークン節約のしくみ |
| [Security & privacy](docs/security.md) | 利用者のルールと、この公開リポジトリの安全チェック |
| [Manual setup](docs/manual-setup.md) | 手動セットアップ（Claude Code 向けにも）とコマンド一覧 |
| [Operations](docs/operations.md) | 最新化、フック、ファイル除外、アンインストール |
| [Explorer page spec](docs/explorer-page-spec.md) | スナップショット形式と同梱ページ |

## コントリビュート

このリポジトリは**公開**です。最初のコミットの前に必ず実行してください：

```sh
sh scripts/install-dev-hooks.sh
```

スナップショット、ログ、トークン、個人のメールアドレス、そして自分専用の禁止語リストに書いた実名を
コミット前にブロックします。CI でも push のたびに同じチェックが走ります。

## ライセンス

MIT（[LICENSE](LICENSE) を参照）
