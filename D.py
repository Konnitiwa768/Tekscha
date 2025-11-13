import os
import time
from playwright.sync_api import sync_playwright

USERNAME = os.getenv("PUP_USER", "")
PASSWORD = os.getenv("PUP_PASS", "")
DOWNLOAD_DIR = "downloads"

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def find_download_button(page):
    """複数の候補セレクタを順に試すぅ"""
    selectors = [
        'button:has-text("Download")',
        'button:has-text("DOWNLOAD")',
        'button:has-text("D")',
        'button:has-text("d")',
        'button[aria-label*="Download"]',
        '[title*="Download"]',
        '[aria-label*="Download"]',
        '[data-tooltip*="Download"]',
        'text=/[Dd]ownload/',
        'text=/^D$/',
        'text=/^d$/',
        'button >> nth=0',  # 最初のボタンを仮に押してみる
    ]
    for sel in selectors:
        btn = page.query_selector(sel)
        if btn:
            print(f"✔ ボタン発見: {sel}")
            return btn
    print("⚠️ どのセレクタでもDボタンが見つかりません。")
    return None


def download_leveldat():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        print("🌐 ログインページへアクセス中...")
        page.goto("https://www.powerupstack.com/auth/login?redirect=/panel/instances/komugi5/files")
        page.wait_for_load_state("networkidle")

        # ログイン入力
        inputs = page.query_selector_all("input")
        if len(inputs) >= 2:
            inputs[0].fill(USERNAME)
            inputs[1].fill(PASSWORD)
            print("✔ ログイン情報入力済み")
        else:
            raise Exception("⚠️ ログイン入力欄が見つかりません")

        login_btn = page.query_selector("button:has-text('Login')")
        if login_btn:
            login_btn.click()
        else:
            inputs[1].press("Enter")

        page.wait_for_load_state("networkidle")
        print("🔑 ログイン成功")

        # level.dat ページへ移動
        target_url = "https://www.powerupstack.com/panel/instances/komugi5/files/edit?path=worlds%2FTUIKA%2Flevel.dat"
        page.goto(target_url)
        page.wait_for_load_state("networkidle")
        print("📄 .dat 編集画面へ移動完了")

        # ボタン探索
        btn = None
        for i in range(5):
            btn = find_download_button(page)
            if btn:
                break
            print("🔁 再探索中…")
            time.sleep(2)
            page.reload()
            page.wait_for_load_state("networkidle")

        if not btn:
            raise Exception("⚠️ D/Downloadボタンが見つかりません。")

        print("⬇️ ダウンロードボタンをクリック中…")
        with page.expect_download(timeout=60000) as download_info:
            btn.click()
        download = download_info.value

        # 保存処理
        save_path = os.path.join(DOWNLOAD_DIR, "level.dat")
        download.save_as(save_path)
        print(f"✅ ダウンロード完了: {save_path}")

        browser.close()


if __name__ == "__main__":
    download_leveldat()
