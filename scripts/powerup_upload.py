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

        # === ステップ2: 認証情報入力（上から1番目、2番目） ===
        print("[STEP] 認証情報入力")
        inputs = page.query_selector_all("input")
        if len(inputs) >= 2:
            inputs[0].fill(USERNAME)
            inputs[1].fill(PASSWORD)
        else:
            raise Exception("入力欄が2つ未満です")
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

        # === ステップ5+6: アップロードボタン押下 + ファイル送信 ===
        print("[STEP] アップロード & ファイル送信")
        upload_btn = page.query_selector('button:has-text("Upload")')
        if upload_btn:
            with page.expect_file_chooser() as fc_info:
                upload_btn.click()
            file_chooser = fc_info.value
            file_chooser.set_files(FILE_PATH)
            time.sleep(2)
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, "05_file_uploaded.png"))
        else:
            print("⚠️ 'Upload' ボタンが見つかりませんでした")

        print("✅ 全ステップ完了")
        browser.close()

if __name__ == "__main__":
    main()
