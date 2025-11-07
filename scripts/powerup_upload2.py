import os
import time
import requests
from playwright.sync_api import sync_playwright

# ===== 設定 =====
API_KEY = "$2a$10$.VBEA/K70RmkFNkXN0tpUut7axu/R/NIkJg6UI0.8QlWCcpxZw1bm"
USERNAME = os.getenv("PUP_USER", "example@example.com")
PASSWORD = os.getenv("PUP_PASS", "password123")

DOWNLOAD_DIR = "downloads"
SCREENSHOT_DIR = "screenshots"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

FILES = [
    {"project_id": 1174972, "file_id": 7173049, "name": "file1.zip"},
    {"project_id": 1152638, "file_id": 6994787, "name": "file2.zip"},
    {"project_id": 1083023, "file_id": 6365190, "name": "file3.zip"},
    {"project_id": 993926, "file_id": 7159195, "name": "file4.zip"}
]


# ===== ユーティリティ =====
def log(msg: str):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")


# ===== CurseForgeダウンロード =====
def download_one(project_id: int, file_id: int, name: str) -> str | None:
    if not API_KEY:
        log("❌ CURSEFORGE_API_KEY が未設定です。")
        return None

    dest = os.path.join(DOWNLOAD_DIR, name)
    if os.path.exists(dest):
        log(f"✔ 既存ファイル検出: {dest}")
        return dest

    url = f"https://api.curseforge.com/v1/mods/{project_id}/files/{file_id}/download-url"
    headers = {"x-api-key": API_KEY}

    log(f"📡 CurseForge: {project_id}/{file_id} URL取得中...")
    r = requests.get(url, headers=headers, timeout=15)
    if r.status_code == 403:
        log("❌ 403 Forbidden — APIキーが無効です。")
        return None
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


# ===== PowerUpStackアップロード =====
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


# ===== メイン（完全逐次） =====
def main():
    if not API_KEY:
        log("❌ 環境変数 CURSEFORGE_API_KEY が未設定です。終了。")
        return

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

        # ---- 完全逐次処理 ----
        for i, f in enumerate(FILES, start=1):
            log(f"\n===== ステップ {i}/{len(FILES)} =====")
            path = download_one(f["project_id"], f["file_id"], f["name"])
            if not path:
                log("⚠️ ダウンロード失敗 → スキップ")
                continue

            ok = upload_one(page, path)
            if ok:
                log(f"🎉 {f['name']} のアップロード完了")
            else:
                log(f"⚠️ {f['name']} のアップロードに失敗")
            time.sleep(4)  # ステップ間のインターバル

        log("\n🌟 すべての段階完了。")
        browser.close()


if __name__ == "__main__":
    main()
