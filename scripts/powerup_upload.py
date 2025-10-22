import os
import time
from playwright.sync_api import sync_playwright

USERNAME = os.getenv("PUP_USER", "example@example.com")
PASSWORD = os.getenv("PUP_PASS", "password123")
FILE_PATH = "Pack/"  # アップロード対象
SCREENSHOT_DIR = "screenshots"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # === ステップ1: ログインページへ ===
        print("[STEP] ログインページへ移動")
        page.goto("https://www.powerupstack.com/auth/login?redirect=/panel/instances/komugi/files?path=resource_packs")
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "01_login_page.png"))

        # === ステップ2: 認証情報入力 ===
        print("[STEP] 認証情報入力")
        page.fill("input[type='email']", USERNAME)
        page.fill("input[type='password']", PASSWORD)
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "02_filled_credentials.png"))

        # === ステップ3: ログインボタン ===
        print("[STEP] ログインボタン押下")
        page.click("button:has-text('Login')")
        page.wait_for_load_state("networkidle")
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "03_after_login.png"))

        # === ステップ4: ファイルページ ===
        print("[STEP] ファイルページへ移動")
        page.goto("https://www.powerupstack.com/panel/instances/komugi/files?path=resource_packs")
        page.wait_for_load_state("networkidle")
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "04_resource_page.png"))

        # === ステップ5: アップロードボタン ===
        print("[STEP] アップロードボタン押下")
        page.click("button:has-text('Upload files')")
        time.sleep(1)
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "05_clicked_upload.png"))

        # === ステップ6: ファイル送信 ===
        print("[STEP] ファイル送信")
        with page.expect_file_chooser() as fc_info:
            page.click("input[type='file']")
        file_chooser = fc_info.value
        file_chooser.set_files(FILE_PATH)
        time.sleep(2)
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "06_file_sent.png"))

        print("✅ 全ステップ完了")
        browser.close()

if __name__ == "__main__":
    main()
