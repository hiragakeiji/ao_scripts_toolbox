# ao Locator Follow Rig Tool

Maya 用の小型ユーティリティツールです。
2つのオブジェクトの間に **Locator + Group** を自動生成し、中間制御用の中間階層（Follow リグ）をワンクリックで構築します。

ドラッグ&ドロップ（D&D）による簡易インストールに対応しており、自動でシェルフにボタンが追加されます。

## ✨ Features

- **自動リグ構築**: Locator + Group を生成し、Parent Constraint で接続します。
- **スナップ機能**: 生成された Group を Selection2（従属側）の位置へ自動スナップ（ワールド行列一致）。
- **Freeze オプション**: UI 上で Transform の Freeze（ON/OFF）が可能。
- **Keep Offset**: すべての Parent Constraint は `Maintain Offset = ON` で作成され、現在の位置関係を維持します。
- **柔軟な選択**: Shape ノードを選択していても、自動で Transform ノードを取得して実行します。
- **Dockable UI**: Maya のワークスペースにドッキング可能な PySide6 ベースの UI。
