import os
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

# ===== 設定 =====
USERNAME = os.getenv("PUP_USER", "example@example.com")
PASSWORD = os.getenv("PUP_PASS", "password123")

# アップロード元ディレクトリ
SOUNDS_DIR = Path("sounds")  # 全 mp3 をここから拾う
JSON_DIR = Path("assets/myaddon/sounds")  # ここにある *.json を拾う

SCREENSHOT_DIR = Path("screenshots")
SCREENSHOT_DIR.mkdir(exist_ok=True)

def log(msg: str):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")

def upload_one(page, path: Path):
    log(f"📤 アップロード開始: {path}")
    try:
        input_box = page.query_selector('input[type="file"]')
        if not input_box:
            log("⚠️ input[type=file]が見つからないのでリロード")
            page.reload()
            page.wait_for_load_state("networkidle")
            input_box = page.query_selector('input[type="file"]')
        if not input_box:
            log("❌ アップロード入力が見つかりません。スキップ")
            return False
        input_box.set_input_files(str(path))
        log(f"✅ ファイル送信済み: {path.name}")
        time.sleep(6)  # アップロード待機（必要に応じて調整）
        # スクリーンショットはファイル名に日時を含めて衝突回避
        shot_name = f"{int(time.time())}_{path.name}.png"
        page.screenshot(path=SCREENSHOT_DIR / shot_name)
        return True
    except Exception as e:
        log(f"⚠️ アップロードエラー: {e}")
        return False

def main():
    # ファイル一覧を収集（mp3 と json）
    mp3_files = sorted(SOUNDS_DIR.glob("*.mp3"))
    json_files = sorted(JSON_DIR.glob("*.json"))

    files = mp3_files + json_files

    if not files:
        log("❌ アップロード対象のファイルが見つかりません。SOUNDS_DIR と JSON_DIR を確認してください。")
        return

    # 存在チェック（念のため）
    for f in files:
        if not f.exists():
            log(f"❌ ファイルが存在しません: {f}")
            return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        log("🌐 PowerUpStack ログインページにアクセス")
        # 必要に応じて redirect URL を修正してください
        page.goto(
            "https://www.powerupstack.com/auth/login?redirect=/panel/instances/komugi5/files?path=resource_packs/RP/sounds"
        )
        page.wait_for_load_state("networkidle")

        inputs = page.query_selector_all("input")
        if len(inputs) >= 2:
            inputs[0].fill(USERNAME)
            inputs[1].fill(PASSWORD)
        login_btn = page.query_selector("button:has-text('Login')")
        if login_btn:
            login_btn.click()
        else:
            # Enter で送信
            inputs[1].press("Enter")

        page.wait_for_load_state("networkidle")
        log("✔ ログイン完了")
        page.screenshot(path=SCREENSHOT_DIR / "login_done.png")

        # 逐次アップロード
        for i, file_path in enumerate(files, start=1):
            log(f"\n===== ステップ {i}/{len(files)} =====")
            ok = upload_one(page, file_path)
            if ok:
                log(f"🎉 {file_path.name} のアップロード完了")
            else:
                log(f"⚠️ {file_path.name} のアップロードに失敗")
            time.sleep(3)

        log("\n🌟 すべての MP3 と JSON のアップロード完了")
        browser.close()

if __name__ == "__main__":
    main()
