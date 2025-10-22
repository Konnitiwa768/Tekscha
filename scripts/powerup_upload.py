import os
import time
from playwright.sync_api import sync_playwright

USERNAME = os.getenv("PUP_USER", "example@example.com")
PASSWORD = os.getenv("PUP_PASS", "password123")
FILE_DIR = "Pack/"  # アップロード対象フォルダ
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
        try:
            btn = page.query_selector(sel)
            if btn:
                print(f"✔ 見つかった: {sel}")
                return btn
        except Exception:
            continue
    print("⚠️ 'U' を含むUpload要素が見つかりません。")
    return None


def find_file_input(page):
    """input[type=file] を探す"""
    try:
        file_input = page.query_selector('input[type="file"]')
        if file_input:
            print("✔ input[type=file] を検出しました。")
            return file_input
    except Exception:
        pass
    print("⚠️ input[type=file] が見つかりません。")
    return None


def collect_files(folder):
    """フォルダ内の全ファイルを再帰的に取得"""
    file_list = []
    for root, _, files in os.walk(folder):
        for f in files:
            full_path = os.path.join(root, f)
            if os.path.isfile(full_path):
                file_list.append(full_path)
    return file_list


def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # headless=False でファイル選択挙動安定
        context = browser.new_context()
        page = context.new_page()

        # === STEP 1: ログインページ ===
        print("[STEP] ログインページへ移動")
        page.goto("https://www.powerupstack.com/auth/login?redirect=/panel/instances/komugi2/files?path=resource_packs")
        page.wait_for_load_state("networkidle")
        page.screenshot(path=f"{SCREENSHOT_DIR}/01_login_page.png")

        print("[STEP] 認証情報入力")
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
            print("⚠️ Loginボタンが見つかりません。Enter送信します。")
            inputs[1].press("Enter")

        page.wait_for_load_state("networkidle")
        time.sleep(2)
        page.screenshot(path=f"{SCREENSHOT_DIR}/02_after_login.png")

        # === STEP 2: ファイルページ ===
        print("[STEP] ファイルページへ移動")
        page.goto("https://www.powerupstack.com/panel/instances/komugi/files?path=resource_packs")
        page.wait_for_load_state("networkidle")
        time.sleep(2)
        page.screenshot(path=f"{SCREENSHOT_DIR}/03_resource_page.png")

        # === STEP 3: Uploadボタン探索 ===
        print("[STEP] Uploadボタン探索")
        upload_btn = None
        for i in range(6):
            upload_btn = find_upload_target(page)
            if upload_btn:
                try:
                    upload_btn.click()
                    print("✔ Uploadボタンクリック成功")
                except Exception:
                    print("⚠️ Uploadボタンクリックに失敗、再試行中…")
                time.sleep(1)
                break
            time.sleep(1)
            page.reload()

        # === STEP 4: ファイル送信 ===
        print("[STEP] input[type=file] 探索・送信")
        file_input = None
        for i in range(6):
            file_input = find_file_input(page)
            if file_input:
                files_to_send = collect_files(FILE_DIR)
                if not files_to_send:
                    raise Exception(f"⚠️ {FILE_DIR} にファイルがありません。")

                print(f"📦 送信対象 {len(files_to_send)} 件:")
                for f in files_to_send:
                    print("   -", f)

                try:
                    file_input.set_input_files(files_to_send)
                    print("✅ ファイル送信完了")
                except Exception as e:
                    print(f"⚠️ set_input_filesでエラー: {e}")
                break
            else:
                print("🔄 input[type=file] 再探索中…")
                time.sleep(1)
                page.reload()

        time.sleep(5)
        page.screenshot(path=f"{SCREENSHOT_DIR}/04_after_upload.png")

        print("🎉 全工程完了")
        browser.close()


if __name__ == "__main__":
    main()
