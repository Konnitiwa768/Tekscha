from python_aternos import Client
import os

# GitHub Secrets からログイン情報
username = os.environ['ATERNOS_USER']
password = os.environ['ATERNOS_PASS']

# サーバログイン
at = Client()
at.login(username, password)

# 最初のサーバを取得
serv = at.list_servers()[0]
fm = serv.files()

# packs フォルダ取得
packs_dir = fm.get_file("/packs")
if not packs_dir.is_dir:
    raise Exception("/packs が見つかりません")

# コピー先のファイル名（ハイフン→アンダーバー）
dst_name = "Bedwars_Mega.mcpack"

# ローカルパス
local_path = "releases/Bedwars_Mega.mcpack"

# サーバ上に既存ファイルがあれば取得、なければ新規作成
try:
    dst_file = fm.get_file(f"/packs/{dst_name}")
    if dst_file is None:
        raise Exception
except:
    dst_file = packs_dir.create(dst_name, "file")  # ここは文字列 'file' で対応

# バイナリ読み込み
with open(local_path, "rb") as f:
    data = f.read()

# サーバ上に書き込み
dst_file.set_content(data)

print(f"{local_path} を /packs/{dst_name} にアップロードしました")
