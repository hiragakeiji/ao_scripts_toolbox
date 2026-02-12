# ao_scripts_toolbox

制作現場・個人制作で使う「小さめの実用スクリプト集」です。  
**ビルド不要 / コピペ配布前提**で、Maya・Houdini・Windows・Python の小物ツールをまとめています。

- English: [README.en.md](README.en.md)
- ツール一覧: [docs/index.md](docs/index.md)

---

## 目的
- 作業の自動化・時短
- 現場で“繰り返し発生する小さな手間”の削減
- 配布・導入が簡単な形で提供（基本は単体スクリプト）

---

各ツールは原則 **1ツール=1フォルダ** で管理します：
- `README.md`（使い方）
- スクリプト本体（`.py` / `.zip` / `.mll` など）
- 必要なら `assets/`（gif/png など）

---

## 使い方（共通）
1. [docs/index.md](docs/index.md) から目的のツールを探す
2. ツールフォルダ内の `README.md` を読む
3. 指示に従って配置・実行する

---

## 注意
- 本リポジトリのツールは **現状優先で更新される**ことがあります。
- 破壊的処理（上書き/削除）がある場合は、各ツールの README に明記します。
- `__pycache__` や `.pyc` などは配布物に不要なためGit管理しません。

---

## ライセンス
MIT License（`LICENSE` を参照）