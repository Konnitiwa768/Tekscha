import os
import time
from playwright.sync_api import sync_playwright

USERNAME = os.getenv("PUP_USER", "example@example.com")
PASSWORD = os.getenv("PUP_PASS", "password123")
DOWNLOAD_DIR = "downloads"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def download_leveldat():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        print("🌐 ログインページへアクセス")
        page.goto("https://www.powerupstack.com/auth/login?redirect=/panel/instances/komugi5/files")
        page.wait_for_load_state("networkidle")

        inputs = page.query_selector_all("input")
        if len(inputs) >= 2:
            inputs[0].fill(USERNAME)
            inputs[1].fill(PASSWORD)
        else:
            raise Exception("⚠️ ログイン入力欄が見つかりません")

        login_btn = page.query_selector("button:has-text('Login')")
        if login_btn:
            login_btn.click()
        else:
            inputs[1].press("Enter")

        page.wait_for_load_state("networkidle")
        print("✔ ログイン成功")

        target_url = "https://www.powerupstack.com/panel/instances/komugi5/files/edit?path=worlds%2FTUIKA%2Flevel.dat"
        page.goto(target_url)
        page.wait_for_load_state("networkidle")
        print("📄 level.dat 編集画面へ移動完了")

        btn = page.query_selector("button:has-text('D'), button:has-text('d')")
        if not btn:
            raise Exception("⚠️ Dボタンが見つかりません")

        print("⬇️ ダウンロードボタンをクリック")
        with page.expect_download() as download_info:
            btn.click()
        download = download_info.value

        save_path = os.path.join(DOWNLOAD_DIR, "level.dat")
        download.save_as(save_path)
        print(f"✅ ダウンロード完了: {save_path}")

        browser.close()

if __name__ == "__main__":
    download_leveldat()
