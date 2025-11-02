import os
import time
import requests
from playwright.sync_api import sync_playwright

USERNAME = os.getenv("PUP_USER", "example@example.com")
PASSWORD = os.getenv("PUP_PASS", "password123")
SCREENSHOT_DIR = "screenshots"
DOWNLOAD_DIR = "downloads"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# ダウンロード対象 URL と保存先　
FILE_URL = "https://github.com/Konnitiwa768/Tekscha/raw/refs/heads/main/releases/Bedwars_Mega.mcpack" #https://www.mediafire.com/file/jxwewlmnam7fm0b/Ymzie_Black.mcpack/file"# 
FILE_NAME = "wow.zip"
FILE_PATH = os.path.join(DOWNLOAD_DIR, FILE_NAME)


def download_file():
    if os.path.exists(FILE_PATH):
        print(f"✔ ファイル既に存在: {FILE_PATH}")
        return

    print(f"📥 ダウンロード開始: {FILE_URL}")
    resp = requests.get(FILE_URL, stream=True)
    resp.raise_for_status()

    with open(FILE_PATH, "wb") as f:
        for chunk in resp.iter_content(8192):
            f.write(chunk)
    print(f"✅ ダウンロード完了: {FILE_PATH}")


def find_upload_target(page):
    selectors = [
        'button:has-text("U")',
        'button:has-text("u")',
        'input[aria-label*="U"]',
        'input[aria-label*="u"]',
        'input[title*="U"]',
        'input[title*="u"]',
        'input[name*="U"]',
        'input[name*="u"]',
        '[class*="U"]',
        '[class*="u"]',
        '[data-tooltip*="U"]',
        '[data-tooltip*="u"]',
        'text=/.*[Uu].*/',
    ]
    for sel in selectors:
        btn = page.query_selector(sel)
        if btn:
            print(f"✔ 見つかった Upload 要素: {sel}")
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


def main():
    download_file()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        context = browser.new_context()
        page = context.new_page()

        # === STEP 1: ログインページ ===
        page.goto(
            "https://www.powerupstack.com/auth/login?redirect=/panel/instances/komugi5/files?path=resource_packs"
        )
        page.wait_for_load_state("networkidle")
        page.screenshot(path=f"{SCREENSHOT_DIR}/01_login_page.png")

        # ログイン情報入力
        inputs = page.query_selector_all("input")
        if len(inputs) >= 2:
            inputs[0].fill(USERNAME)
            inputs[1].fill(PASSWORD)
            print("✔ ログイン情報入力完了")
        else:
            raise Exception("⚠️ 入力欄が2つ未満です。")

        # ログインボタン押下
        login_btn = page.query_selector("button:has-text('Login')")
        if login_btn:
            login_btn.click()
        else:
            inputs[1].press("Enter")

        page.wait_for_load_state("networkidle")
        time.sleep(2)
        page.screenshot(path=f"{SCREENSHOT_DIR}/02_after_login.png")

        # === STEP 2: Uploadボタン探索 ===
        upload_btn = None
        for i in range(5):
            upload_btn = find_upload_target(page)
            if upload_btn:
                upload_btn.click()
                print("✔ Uploadボタンクリック成功")
                time.sleep(1)
                break
            time.sleep(1)
            page.reload()

        # === STEP 3: ファイル送信 ===
        file_input = None
        for i in range(5):
            file_input = find_file_input(page)
            if file_input:
                try:
                    file_input.set_input_files(FILE_PATH)
                    print(f"✅ ファイル送信完了: {FILE_PATH}")
                except Exception as e:
                    print(f"⚠️ set_input_filesでエラー: {e}")
                break
            time.sleep(1)
            page.reload()

        time.sleep(30)
        page.screenshot(path=f"{SCREENSHOT_DIR}/03_after_upload.png")
        print("🎉 アップロード完了")
        browser.close()


if __name__ == "__main__":
    main()
