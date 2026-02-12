# ao Locator Follow Rig Tool

Maya 用の小型ユーティリティツールです。
2つのオブジェクトの間に **Locator + Group** を自動生成し、中間制御用の中間階層（Follow リグ）をワンクリックで構築します。

ドラッグ&ドロップ（D&D）による簡易インストールに対応しており、自動でシェルフにボタンが追加されます。

## Features / 機能

- Locator + Group の自動生成
- Group を Selection2 にスナップ
- **Freeze Transform を UI で ON/OFF**
- Parent Constraint（すべて **Keep Offset = ON**）
  - Selection1 → Group
  - Locator → Selection2
- Shape 選択でも動作（自動で transform を取得）
- Dockable UI（Maya WorkspaceControl）
- D&D インストーラー同梱（配布向け）

## Usage / 使い方

### 1) Install (Drag & Drop) / インストール（D&D）

2. `ao_LocatorFollowRigTool.zip` をダウンロード、解凍
2. `ao_LocatorFollowRigTool_download.py` を Maya のビューポートへドラッグ&ドロップ  
3. Shelf「tool」にボタンが追加されます  
4. ボタンを押して UI を開きます

> 既にボタンがある場合は置き換え（更新）されます。

### 2) Run / 実行

1. **Selection1 → Selection2 の順で 2 つ選択**
2. UI の `apply` を押す
3. 必要なら「ロケーターのフリーズ」を ON/OFF

---

## Files / 構成
- ao_LocatorFollowRigTool_UI.py # UI（PySide6 / Dockable）
- ao_LocatorFollowRigTool_system.py # ロジック
- ao_LocatorFollowRigTool_download.py # D&D インストーラー
- ao_LocatorFollowRigTool_icon.png # アイコン

---

## Requirements / 動作環境

- Autodesk Maya 2025
- Python 3.x (Maya 同梱)
- PySide6（Maya 2025 同梱）

---

## Author

Hiraga Keiji