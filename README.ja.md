# muse-repo-explorer

[English](README.md) | **日本語** | [简体中文](README.zh-CN.md) | [한국어](README.ko.md)

Muse（パーソナルAIエージェント）の環境に GitHub リポジトリをローカル clone しておき、

- **Muse はローカルからコードを読む** — コネクタ経由より速く、トークン消費も少ない
- **あなたはスマホからコードを読む** — スナップショットを埋め込んだ自分専用の「ファイルエクスプローラー」ページ（Muse のスペース）で

という運用の仕組み一式です。

## はじめかた：これを Muse に貼るだけ

下のブロックを丸ごとコピーして Muse に送ってください。途中で確認されるのは
(1) GitHub ログインのワンタイムコード入力、(2) clone するリポジトリの範囲、の2点だけです。

````text
「muse-repo-explorer」（https://github.com/masato-umeno/muse-repo-explorer）の仕組みを私の環境に構築してください。最後のプライバシールールを厳守してください。

1. ツールのインストール（VM が入れ替わっても残るよう、ホームディレクトリ配下に置く）
   - ghq の最新リリースバイナリ（github.com/x-motemen/ghq）を ~/.local/bin/ghq に配置する。
   - gh（GitHub CLI）の最新リリースバイナリ（github.com/cli/cli）を ~/.local/bin/gh に配置する。
   - それぞれ --version で動作確認する。

2. GitHub 認証（デバイスフロー、HTTPS のみ）
   - `gh auth login --hostname github.com --git-protocol https --web` を実行する。
   - ワンタイムコードと https://github.com/login/device を私に見せ、私がブラウザで承認するまで待つ。
   - 完了後、`gh auth status` のアカウント名を報告し、`gh auth setup-git` を実行する。
   - SSH は使わない。パスワードやトークンを私に貼らせないこと。

3. リポジトリの clone
   - 私がアクセスできるリポジトリ（`gh repo list`、所属組織を含む）を一覧し、どれを clone するか確認してから `ghq get <owner>/<repo>` で取得する。
   - アーカイブ済みリポジトリは、希望がなければ対象外にする。

4. スナップショットツールの配置
   - `ghq get https://github.com/masato-umeno/muse-repo-explorer` を実行する。
   - その tools/ の中身をすべて ~/workspace/repo-explorer/（git リポジトリの外）にコピーし、スクリプトに実行権限を付ける。
   - `python3 ~/workspace/repo-explorer/update_snapshot.py` を実行し、snapshot.json ができることを確認する。
   - ページに表示したくないファイル（例：`.env*`、`*.pem`、`secrets/*`）があるか私に確認し、あれば ~/workspace/repo-explorer/exclude.txt に glob を書いて update_snapshot.py を再実行する。

5. pull フックの導入
   - `~/workspace/repo-explorer/install-hooks.sh` を実行する。
   - どれか1つのリポジトリで pull し、snapshot.json が再生成されたことを確認する。

6. 閲覧ページ（Muse のスペース）の作成
   - そのリポジトリの docs/explorer-page-spec.md に従って作る。snapshot.json は単一の独立したアセットにし、差し替えだけで最新化できる構造にする。
   - ページの UI は私の言語にする。
   - ページは非公開のままにし、公開リンクは絶対に作らない。

7. 最新化
   - 私が「エクスプローラーを最新化して」と言ったら、update_snapshot.py → sync_status.py の順に実行する。sync_status.py の終了コードが 10 のときだけページのスナップショットを差し替え、その後 `sync_status.py --mark` を実行する。
   - 任意：週次チェックなど既存の定期ジョブがあれば、その最後にこの最新化手順を相乗りさせてよい（チャット報告は不要）。

8. 完了報告
   - `ghq list` の結果、スナップショットのサイズ、作成したページ、失敗したものとその理由。

プライバシールール：
- snapshot.json を git 管理下・公開リポジトリ・ファイル共有サービスに置かない。
- 閲覧ページを公開共有しない。
- 認証情報（パスワード、トークン）をチャット・ファイル・ログに残さない。
- clone するのは、私が正当なアクセス権を持つリポジトリだけ。
````

## 始める前に — 3つのルール

1. **スナップショットはソースコードそのもの。** `snapshot.json` を git にも共有先にも置かない。
2. **閲覧ページは非公開のまま。** 公開リンクを作ると、リンクを知る誰でもコードを読めてしまう。
3. **ログインはデバイスフローだけ。** GitHub のパスワードやトークンをチャットに貼らない。

詳しくは [docs/security.md](docs/security.md)（英語）

## ドキュメント（英語）

| ドキュメント | 内容 |
| --- | --- |
| [How it works](docs/design.md) | 全体像と設計判断 |
| [Security & privacy](docs/security.md) | 利用者のルールと、この公開リポジトリの安全チェック |
| [Manual setup](docs/manual-setup.md) | プロンプトを使わない手動セットアップ（Claude Code 向けにも） |
| [Operations](docs/operations.md) | 最新化、フック、ファイル除外、アンインストール |
| [Explorer page spec](docs/explorer-page-spec.md) | スナップショット形式とページの UI 仕様 |

## コントリビュート

このリポジトリは**公開**です。最初のコミットの前に必ず実行してください：

```sh
sh scripts/install-dev-hooks.sh
```

スナップショット、ログ、トークン、個人のメールアドレス、そして自分専用の禁止語リストに書いた実名を
コミット前にブロックします。CI でも push のたびに同じチェックが走ります。

## ライセンス

MIT（[LICENSE](LICENSE) を参照）
