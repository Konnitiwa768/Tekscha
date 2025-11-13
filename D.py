import os
import time
import requests
from playwright.sync_api import sync_playwright

USERNAME = os.getenv("PUP_USER", "")
PASSWORD = os.getenv("PUP_PASS", "")
DOWNLOAD_DIR = "downloads"
HEADLESS = True  # FalseにするとGUI表示で挙動確認できる

os.makedirs(DOWNLOAD_DIR, exist_ok=True)


def find_download_button(page):
    """複数の候補セレクタを順に試す"""
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
        'a[download]',
        'a[href*="download"]',
        'button >> nth=0',  # fallback
    ]
    for sel in selectors:
        btn = page.query_selector(sel)
        if btn:
            print(f"✔ ボタン発見: {sel}")
            return btn
    print("⚠️ どのセレクタでもDボタンが見つかりません。")
    return None


def try_direct_download(context, target_url):
    """Cookieを引き継いで直接HTTPでダウンロードを試す"""
    print("🌐 HTTP直ダウンロードを試行中...")
    cookies = context.cookies()
    headers = {
        "Cookie": "; ".join([f"{c['name']}={c['value']}" for c in cookies])
    }
    # サイト構成に応じて修正可能
    dl_url = (
        "https://www.powerupstack.com/panel/instances/komugi5/files/"
        "download?path=worlds%2FTUIKA%2Flevel.dat"
    )

    resp = requests.get(dl_url, headers=headers)
    if resp.status_code == 200 and resp.content:
        save_path = os.path.join(DOWNLOAD_DIR, "level.dat")
        with open(save_path, "wb") as f:
            f.write(resp.content)
        print(f"✅ HTTP直ダウンロード成功: {save_path}")
        return True
    else:
        print(f"❌ HTTP直ダウンロード失敗: {resp.status_code}")
        return False


def download_leveldat():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=HEADLESS, slow_mo=150 if not HEADLESS else 0)
        context = browser.new_context(accept_downloads=True)
        page = context.new_page()

        print("🌐 ログインページへアクセス中...")
        page.goto("https://www.powerupstack.com/auth/login?redirect=/panel/instances/komugi5/files")
        page.wait_for_load_state("networkidle")

        # ログイン
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

        # level.dat ページへ
        target_url = (
            "https://www.powerupstack.com/panel/instances/komugi5/files/"
            "edit?path=worlds%2FTUIKA%2Flevel.dat"
        )
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
            print("⚠️ Dボタンが見つからないためHTTP直取得に切替")
            if not try_direct_download(context, target_url):
                raise Exception("❌ どの方法でも取得に失敗しました。")
            browser.close()
            return

        # ダウンロード監視設定
        download_path = os.path.join(DOWNLOAD_DIR, "level.dat")
        downloaded = False

        def handle_download(download):
            nonlocal downloaded
            download.save_as(download_path)
            downloaded = True
            print(f"✅ ダウンロード完了(イベントキャッチ): {download_path}")

        context.on("download", handle_download)

        print("⬇️ ダウンロードボタンをクリック中…")
        try:
            with page.expect_download(timeout=30000) as download_info:
                btn.click()
            download = download_info.value
            download.save_as(download_path)
            print(f"✅ ダウンロード完了(expect_download): {download_path}")
            downloaded = True
        except Exception as e:
            print(f"⚠️ expect_download失敗: {e}")
            # イベント監視のほうで拾える可能性あり
            page.wait_for_timeout(8000)

        if not downloaded:
            print("❌ ダウンロードイベントを検知できません。HTTP直取得に切替。")
            try_direct_download(context, target_url)

        # デバッグ: ページ内容保存
        page.screenshot(path=os.path.join(DOWNLOAD_DIR, "page_state.png"))
        with open(os.path.join(DOWNLOAD_DIR, "page_source.html"), "w", encoding="utf-8") as f:
            f.write(page.content())

        browser.close()


if __name__ == "__main__":
    download_leveldat()
