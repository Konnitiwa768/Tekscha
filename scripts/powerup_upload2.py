import os
import time
import requests
from playwright.sync_api import sync_playwright

# ===== 設定 =====
API_KEY = os.getenv("CURSEFORGE_API_KEY", "YOUR_API_KEY_HERE")
USERNAME = os.getenv("PUP_USER", "example@example.com")
PASSWORD = os.getenv("PUP_PASS", "password123")
SCREENSHOT_DIR = "screenshots"
DOWNLOAD_DIR = "downloads"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ===== 対象ファイルリスト =====
FILES = [
    {"project_id": 1174972, "file_id": 7173049, "name": "file1_curseforge.zip"},
    {"project_id": 1152638, "file_id": 6994787, "name": "file2_curseforge.zip"},
    {"project_id": 1083023, "file_id": 6365190, "name": "file3_curseforge.zip"},
]


# ===== CurseForgeダウンロード関数 =====
def download_from_curseforge(project_id, file_id, filename):
    file_path = os.path.join(DOWNLOAD_DIR, filename)

    if os.path.exists(file_path):
        print(f"✔ 既に存在: {file_path}")
        return file_path

    print(f"📡 CurseForgeからダウンロードURL取得中: project={project_id}, file={file_id}")
    url = f"https://api.curseforge.com/v1/mods/{project_id}/files/{file_id}/download-url"
    headers = {"x-api-key": API_KEY}

    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        raise Exception(f"URL取得失敗: {resp.status_code} {resp.text}")

    download_url = resp.json().get("data")
    if not download_url:
        raise Exception("ダウンロードURLを取得できませんでした。")

    print(f"📥 ダウンロード開始: {download_url}")
    r = requests.get(download_url, stream=True)
    r.raise_for_status()

    with open(file_path, "wb") as f:
        for chunk in r.iter_content(8192):
            f.write(chunk)
    print(f"✅ ダウンロード完了: {file_path}")
    return file_path


# ===== Upload要素探索 =====
def find_upload_target(page):
    selectors = [
        'button:has-text("U")', 'button:has-text("u")',
        'input[aria-label*="U"]', 'input[aria-label*="u"]',
        'input[title*="U"]', 'input[title*="u"]',
        'input[name*="U"]', 'input[name*="u"]',
        '[class*="U"]', '[class*="u"]',
        '[data-tooltip*="U"]', '[data-tooltip*="u"]',
        'text=/.*[Uu].*/',
    ]
    for sel in selectors:
        btn = page.query_selector(sel)
        if btn:
            print(f"✔ Upload要素検出: {sel}")
            return btn
    print("⚠️ Upload要素が見つかりません。")
    return None


def find_file_input(page):
    file_input = page.query_selector('input[type="file"]')
    if file_input:
        print("✔ input[type=file] 検出")
        return file_input
    print("⚠️ input[type=file] が見つかりません")
    return None


# ===== PowerUpStackアップロード関数 =====
def upload_to_powerupstack(files):
    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        page = context.new_page()

        print("🌐 ログインページへアクセス中...")
        page.goto("https://www.powerupstack.com/auth/login?redirect=/panel/instances/komugi5/files?path=behavior_packs")
        page.wait_for_load_state("networkidle")
        page.screenshot(path=f"{SCREENSHOT_DIR}/01_login_page.png")

        # ログイン
        inputs = page.query_selector_all("input")
        if len(inputs) >= 2:
            inputs[0].fill(USERNAME)
            inputs[1].fill(PASSWORD)
            print("✔ ログイン情報入力完了")
        else:
            raise Exception("⚠️ 入力欄が2つ未満です。")

        login_btn = page.query_selector("button:has-text('Login')")
        if login_btn:
            login_btn.click()
        else:
            inputs[1].press("Enter")

        page.wait_for_load_state("networkidle")
        time.sleep(2)
        page.screenshot(path=f"{SCREENSHOT_DIR}/02_after_login.png")

        # 各ファイルを順番にアップロード
        for i, path in enumerate(files, start=1):
            print(f"📤 アップロード開始: {path}")
            for retry in range(5):
                upload_btn = find_upload_target(page)
                if upload_btn:
                    upload_btn.click()
                    print("✔ Uploadボタンクリック成功")
                    time.sleep(1)
                    break
                time.sleep(1)
                page.reload()

            file_input = None
            for retry in range(5):
                file_input = find_file_input(page)
                if file_input:
                    try:
                        file_input.set_input_files(path)
                        print(f"✅ ファイル送信完了: {path}")
                    except Exception as e:
                        print(f"⚠️ set_input_filesでエラー: {e}")
                    break
                time.sleep(1)
                page.reload()

            time.sleep(10)
            page.screenshot(path=f"{SCREENSHOT_DIR}/upload_{i}.png")

        print("🎉 すべてのファイルをアップロード完了")
        browser.close()


# ===== メイン =====
def main():
    paths = []
    for f in FILES:
        path = download_from_curseforge(f["project_id"], f["file_id"], f["name"])
        paths.append(path)

    upload_to_powerupstack(paths)


if __name__ == "__main__":
    main()
