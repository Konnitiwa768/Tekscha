import os
import time
from playwright.sync_api import sync_playwright

USERNAME = os.getenv("PUP_USER", "example@example.com")
PASSWORD = os.getenv("PUP_PASS", "password123")
FILE_PATH = "Pack/"
SCREENSHOT_DIR = "screenshots"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def find_upload_target(page):
    """
    'u'または'U'を含むボタン・inputを広く探索して返す。
    text, aria-label, title, class, name, data属性などを包括。
    """
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
            print(f"✔ 見つかった: {sel}")
            return btn
    print("⚠️ 'U'を含むUpload要素が見つかりません。")
    return None


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        # === STEP 1: ログインページ ===
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

        # === STEP 2: ファイルページ ===
        print("[STEP] ファイルページへ移動")
        page.goto("https://www.powerupstack.com/panel/instances/komugi/files?path=resource_packs")
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        page.screenshot(path=f"{SCREENSHOT_DIR}/03_resource_page.png")

        # === STEP 3: Uploadターゲット検出 ===
        print("[STEP] Upload関連要素探索開始")
        upload_btn = None
        for i in range(5):
            upload_btn = find_upload_target(page)
            if upload_btn:
                break
            time.sleep(1)
            page.reload()

        if not upload_btn:
            raise Exception("⚠️ Uploadボタン/入力欄が見つかりませんでした。")

        # === STEP 4: ファイル選択 ===
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
