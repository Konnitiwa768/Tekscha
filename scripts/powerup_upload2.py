import os
import time
import zipfile
import shutil
import requests
from playwright.sync_api import sync_playwright

# ===== 設定 =====
API_KEY = "$2a$10$.VBEA/K70RmkFNkXN0tpUut7axu/R/NIkJg6UI0.8QlWCcpxZw1bm"
USERNAME = os.getenv("PUP_USER", "example@example.com")
PASSWORD = os.getenv("PUP_PASS", "password123")

DOWNLOAD_DIR = "downloads"
SCREENSHOT_DIR = "screenshots"
TEMP_DIR = "temp_unpack"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

FILES = [
    {"project_id": 1174972, "file_id": 7173049, "name": "file1.zip"},
    {"project_id": 1152638, "file_id": 6994787, "name": "file2.zip"},
    {"project_id": 1083023, "file_id": 6365190, "name": "file3.zip"},
    {"project_id": 993926, "file_id": 7159195, "name": "file4.zip"},
    {"project_id": 1364457, "file_id": 7198015, "name": "file9.zip"},
]


def log(msg: str):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")


# ===== ダウンロード =====
def download_one(project_id: int, file_id: int, name: str) -> str | None:
    dest = os.path.join(DOWNLOAD_DIR, name)
    if os.path.exists(dest):
        log(f"✔ 既存ファイル検出: {dest}")
        return dest

    url = f"https://api.curseforge.com/v1/mods/{project_id}/files/{file_id}/download-url"
    headers = {"x-api-key": API_KEY}
    log(f"📡 CurseForge: {project_id}/{file_id} URL取得中...")
    r = requests.get(url, headers=headers, timeout=15)
    if r.status_code != 200:
        log(f"⚠️ URL取得失敗: {r.status_code}")
        return None

    dl = r.json().get("data")
    if not dl:
        log("⚠️ URLデータが空です。")
        return None

    log(f"⬇️ ダウンロード開始: {dl}")
    with requests.get(dl, stream=True, timeout=60) as resp:
        resp.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in resp.iter_content(8192):
                f.write(chunk)
    log(f"✅ ダウンロード完了: {dest}")
    return dest


# ===== file9 特殊処理 =====
def process_file9(zip_path: str) -> list[str]:
    log(f"🧩 特殊処理: {zip_path} を展開中…")

    temp_root = os.path.join(TEMP_DIR, "file9_work")
    if os.path.exists(temp_root):
        shutil.rmtree(temp_root)
    os.makedirs(temp_root)

    # 第一段階: file9.zip 展開
    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(temp_root)
    log("📦 file9.zip 展開完了")

    output_files = []

    # 中の .mcpack をそれぞれ展開
    for item in os.listdir(temp_root):
        if not item.endswith(".mcpack"):
            continue
        mcpack_path = os.path.join(temp_root, item)
        name_without_ext = os.path.splitext(item)[0]
        mcpack_extract_dir = os.path.join(temp_root, f"{name_without_ext}_unpack")
        os.makedirs(mcpack_extract_dir, exist_ok=True)

        with zipfile.ZipFile(mcpack_path, "r") as z:
            z.extractall(mcpack_extract_dir)
        log(f"📂 {item} 展開完了")

        # 直下に render_controllers や manifest.json がある → 再構成が必要
        contents = os.listdir(mcpack_extract_dir)
        has_loose_root = any(
            os.path.isfile(os.path.join(mcpack_extract_dir, f)) or os.path.isdir(os.path.join(mcpack_extract_dir, f))
            for f in contents
        )

        # 正しいフォルダ構造にまとめる
        rebuilt_dir = os.path.join(temp_root, name_without_ext)
        if os.path.exists(rebuilt_dir):
            shutil.rmtree(rebuilt_dir)
        os.makedirs(rebuilt_dir)

        for entry in contents:
            src = os.path.join(mcpack_extract_dir, entry)
            dst = os.path.join(rebuilt_dir, entry)
            shutil.move(src, dst)
        log(f"📁 構成整形済み: {rebuilt_dir}")

        # zipとして再作成
        rebuilt_zip = os.path.join(DOWNLOAD_DIR, f"{name_without_ext}.zip")
        if os.path.exists(rebuilt_zip):
            os.remove(rebuilt_zip)
        shutil.make_archive(rebuilt_zip.replace(".zip", ""), "zip", rebuilt_dir)
        log(f"🗜 再構成zip作成: {rebuilt_zip}")
        output_files.append(rebuilt_zip)

    log(f"✅ file9特殊処理完了: {output_files}")
    return output_files


# ===== アップロード =====
def upload_one(page, path: str):
    log(f"📤 アップロード開始: {path}")
    try:
        input_box = page.query_selector('input[type="file"]')
        if not input_box:
            log("⚠️ input[type=file]が見つからないためリロード")
            page.reload()
            page.wait_for_load_state("networkidle")
            input_box = page.query_selector('input[type="file"]')

        if not input_box:
            log("❌ アップロード入力が見つかりません。スキップ。")
            return False

        input_box.set_input_files(path)
        log(f"✅ ファイル送信済み: {os.path.basename(path)}")
        time.sleep(8)
        page.screenshot(path=f"{SCREENSHOT_DIR}/{os.path.basename(path)}.png")
        return True
    except Exception as e:
        log(f"⚠️ アップロードエラー: {e}")
        return False


# ===== メイン =====
def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        log("🌐 PowerUpStackログインページへアクセス")
        page.goto("https://www.powerupstack.com/auth/login?redirect=/panel/instances/komugi5/files?path=resource_packs")
        page.wait_for_load_state("networkidle")

        inputs = page.query_selector_all("input")
        if len(inputs) >= 2:
            inputs[0].fill(USERNAME)
            inputs[1].fill(PASSWORD)
        login_btn = page.query_selector("button:has-text('Login')")
        if login_btn:
            login_btn.click()
        else:
            inputs[1].press("Enter")

        page.wait_for_load_state("networkidle")
        log("✔ ログイン完了")
        page.screenshot(path=f"{SCREENSHOT_DIR}/login_done.png")

        for i, f in enumerate(FILES, start=1):
            log(f"\n===== ステップ {i}/{len(FILES)} =====")
            path = download_one(f["project_id"], f["file_id"], f["name"])
            if not path:
                log("⚠️ ダウンロード失敗 → スキップ")
                continue

            # file9のみ特殊処理
            if f["name"] == "file9.zip":
                extracted_files = process_file9(path)
                for ef in extracted_files:
                    upload_one(page, ef)
                    time.sleep(4)
            else:
                upload_one(page, path)
                time.sleep(4)

        log("\n🌟 すべての段階完了。")
        browser.close()


if __name__ == "__main__":
    main()
