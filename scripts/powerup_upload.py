import os
import time
from playwright.sync_api import sync_playwright

USERNAME = os.getenv("PUP_USER", "example@example.com")
PASSWORD = os.getenv("PUP_PASS", "password123")
FILE_PATH = "Pack/"
SCREENSHOT_DIR = "screenshots"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def find_upload_button(page):
    """Upload ボタンを探して返す（複数パターンで検索）"""
    selectors = [
        'button:has-text("Upload")',
        'text="Upload"',
        '[aria-label*="Upload"]',
        '[title*="Upload"]',
        '[data-tooltip*="Upload"]',
        '[class*="upload"]',
        'button:has-text("UPLOAD")',
        'button:has-text("アップロード")',
        'text="アップロード"',
    ]
    for sel in selectors:
        btn = page.query_selector(sel)
        if btn:
            print(f"✔ 見つかった: {sel}")
            return btn
    print("⚠️ Uploadボタンが見つかりません。")
    return None


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # === ステップ1: ログイン ===
        print("[STEP] ログインページへ移動")
        page.goto("https://www.powerupstack.com/auth/login?redirect=/panel/instances/komugi/files?path=resource_packs")
        page.screenshot(path=f"{SCREENSHOT_DIR}/01_login_page.png")

        print("[STEP] 認証情報入力")
        inputs = page.query_selector_all("input")
        if len(inputs) >= 2:
            inputs[0].fill(USERNAME)
            inputs[1].fill(PASSWORD)
        else:
            raise Exception("⚠️ 入力欄が2つ未満です。")

        page.click("button:has-text('Login')")
        page.wait_for_load_state("networkidle")
        page.screenshot(path=f"{SCREENSHOT_DIR}/02_after_login.png")

        # === ステップ2: ファイルページへ ===
        print("[STEP] ファイルページへ移動")
        page.goto("https://www.powerupstack.com/panel/instances/komugi/files?path=resource_packs")
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        page.screenshot(path=f"{SCREENSHOT_DIR}/03_resource_page.png")

        # === ステップ3: Upload検出＆送信 ===
        print("[STEP] Uploadボタン探索開始")
        upload_btn = None
        for i in range(5):  # 5回リトライ
            upload_btn = find_upload_button(page)
            if upload_btn:
                break
            time.sleep(1)
            page.reload()
        if not upload_btn:
            raise Exception("Uploadボタンが見つかりませんでした。")

        # === ステップ4: ファイル選択 ===
        print("[STEP] ファイルアップロード開始")
        with page.expect_file_chooser() as fc_info:
            upload_btn.click()
        file_chooser = fc_info.value
        file_chooser.set_files(FILE_PATH)
        print("✔ ファイル選択完了")

        time.sleep(3)
        page.screenshot(path=f"{SCREENSHOT_DIR}/04_after_upload.png")

        print("✅ 全工程完了")
        browser.close()


if __name__ == "__main__":
    main()
