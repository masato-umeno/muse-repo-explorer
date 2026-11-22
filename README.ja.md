# muse-repo-viewer

[English](README.md) | **日本語** | [简体中文](README.zh-CN.md) | [한국어](README.ko.md)

Muse で動くリポジトリビューアです。GitHub リポジトリのローカル clone を Muse の環境に保持し、次のことができるようにします。

- **利用者は**、Muse の非公開スペースで、スマホからコードを読んだり検索したりできます。選んだ行について Muse に質問することもできます。
- **Muse は**、ソースコードをローカルのファイルから読みます。コネクタ経由より速く、トークンの消費も少なく済みます。

紹介ページ：<https://masato-umeno.github.io/muse-repo-viewer/>

## セットアップ

次の1行を Muse にコピペしてください。Muse はいつもの言語で応答を続けます。

```text
Set up muse-repo-viewer for me by following https://github.com/masato-umeno/muse-repo-viewer/blob/main/MUSE_SETUP.md (keep replying in the language we normally use)
```

途中で、GitHub へのサインインの承認と、対象リポジトリの選択を求められます（このリポジトリをサンプルとして使えます）。スペースの作成前などに続けてよいか確認されたら、「進めて」と返してください。あとで更新するときも、同じ1行を送ります。

## 使い方

- **最新化：** Muse に「ビューアを最新化して」と頼みます。アップロードされるのは、新しいコミットがあったリポジトリだけです。
- **リポジトリの追加：** Muse に clone を頼んでから、最新化します。
- **ファイルの非表示：** `~/workspace/repo-viewer/exclude.txt` に `.env*` などの glob パターンを書きます。
- **表示言語：** ページの設定（歯車ボタン）で変えられます。

## セキュリティ

スペースには、対象リポジトリのソースコードがすべて入ります。非公開のまま使ってください。セットアップの1行は、このリポジトリに置かれた指示に Muse を従わせます。バージョンを固定する場合は、URL の `main` をコミット ID かタグに置き換えてください。詳しくは[セキュリティ](docs/security.md)を参照してください。

## ドキュメント

ドキュメントは英語で記述しています。

| ドキュメント | 内容 |
| --- | --- |
| [アーキテクチャ](docs/architecture.md) | 構成要素、データの流れ、設計判断、トークン効率 |
| [セキュリティ](docs/security.md) | 扱うデータ、組み込みの保護機能、利用者向けの推奨事項 |
| [手動セットアップ](docs/manual-setup.md) | プロンプトを使わずに直接、または Claude Code で構築する手順 |
| [運用](docs/operations.md) | 最新化、保守、トラブルシューティング、アンインストール |
| [リファレンス](docs/reference.md) | コマンド、設定、状態ファイル、スナップショット形式 |
| [ビューアページ](docs/page.md) | 同梱ページの提供形式と動作 |

## コントリビュート

このリポジトリは公開されています。最初のコミットの前に [CONTRIBUTING.md](CONTRIBUTING.md) をお読みください。

## ライセンス

[MIT](LICENSE)
