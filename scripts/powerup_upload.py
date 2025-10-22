import os
import time
from playwright.sync_api import sync_playwright

USERNAME = os.getenv("PUP_USER", "example@example.com")
PASSWORD = os.getenv("PUP_PASS", "password123")
FILE_DIR = "Pack/"  # フォルダ指定
SCREENSHOT_DIR = "screenshots"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def find_upload_target(page):
    """'u' または 'U' を含むボタン・inputを広く探索"""
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
    print("⚠️ 'U' を含むUpload要素が見つかりません。")
    return None


def find_file_input(page):
    """input[type=file] を探す"""
    file_input = page.query_selector('input[type="file"]')
    if file_input:
        print("✔ input[type=file] を検出しました。")
        return file_input
    print("⚠️ input[type=file] が見つかりません。")
    return None


def collect_files(folder):
    """フォルダ内の全ファイルを再帰的に取得"""
    file_list = []
    for root, _, files in os.walk(folder):
        for f in files:
            full_path = os.path.join(root, f)
            file_list.append(full_path)
    return file_list


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

        # === STEP 3: Uploadボタン ===
        print("[STEP] Uploadボタン探索")
        upload_btn = None
        for i in range(5):
            upload_btn = find_upload_target(page)
            if upload_btn:
                upload_btn.click()
                time.sleep(1)
                break
            time.sleep(1)
            page.reload()

        # === STEP 4: ファイル送信 ===
        print("[STEP] input[type=file] 探索・送信")
        file_input = None
        for i in range(5):
            file_input = find_file_input(page)
            if file_input:
                files_to_send = collect_files(FILE_DIR)
                if not files_to_send:
                    raise Exception(f"⚠️ {FILE_DIR} にファイルがありません。")
                file_input.set_input_files(files_to_send)
                print(f"✔ ファイル送信完了 ({len(files_to_send)} 件)")
                for f in files_to_send:
                    print("  -", f)
                break
            time.sleep(1)
            page.reload()

        time.sleep(3)
        page.screenshot(path=f"{SCREENSHOT_DIR}/04_after_upload.png")

        print("✅ 全工程完了")
        browser.close()


if __name__ == "__main__":
    main()
