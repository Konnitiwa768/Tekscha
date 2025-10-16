from python_aternos import Client, FileType

# GitHub Actions ではシークレットに設定した値を利用
import os

username = os.environ['ATERNOS_USER']
password = os.environ['ATERNOS_PASS']

at = Client()
at.login(username, password)

serv = at.list_servers()[0]
fm = serv.files()

# コピー先の packs フォルダ
packs_dir = fm.get_file("/packs")
if not packs_dir.is_dir:
    raise Exception("/packs が見つかりません")

# コピー先ファイル名
dst_name = "packs/Bedwars_Mega.mcpack"

# ファイル作成
dst_file = packs_dir.create(dst_name, FileType.file)

# リポジトリのパス
local_path = "releases/Bedwars_Mega.mcpack"

with open(local_path, "rb") as f:
    data = f.read()

# バイナリを書き込む
dst_file.set_content(data)

print(f"{local_path} を /packs/{dst_name} にアップロードしました")
