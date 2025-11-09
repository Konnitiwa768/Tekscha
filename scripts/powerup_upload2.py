import os
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

# ===== 設定 =====
USERNAME = os.getenv("PUP_USER", "example@example.com")
PASSWORD = os.getenv("PUP_PASS", "password123")

# 手作業で生成・配置したファイルのパス
UPLOAD_DIR = Path("resource_packs/RP/sounds")
SCREENSHOT_DIR = Path("screenshots")
SCREENSHOT_DIR.mkdir(exist_ok=True)

# ファイルを1つずつ手動で指定する場合
files = [
    UPLOAD_DIR / "phyle_idle.mp3",
    UPLOAD_DIR / "phyle_hurt.mp3",
    UPLOAD_DIR / "phyle_death.mp3",
    UPLOAD_DIR / "troivjuer_idle.mp3",
    UPLOAD_DIR / "troivjuer_hurt.mp3",
    UPLOAD_DIR / "troivjuer_death.mp3",
    UPLOAD_DIR / "nihdun_idle.mp3",
    UPLOAD_DIR / "nihdun_hurt.mp3",
    UPLOAD_DIR / "nihdun_death.mp3",
    UPLOAD_DIR / "sounds.json",
]

def log(msg: str):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")

def upload_one(page, path: Path):
    log(f"📤 アップロード開始: {path.name}")
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
        time.sleep(6)  # アップロード待機
        page.screenshot(path=SCREENSHOT_DIR / f"{path.name}.png")
        return True
    except Exception as e:
        log(f"⚠️ アップロードエラー: {e}")
        return False

def main():
    # ファイル存在チェック
    for f in files:
        if not f.exists():
            log(f"❌ ファイルが存在しません: {f}")
            return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        log("🌐 PowerUpStack ログインページにアクセス")
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

        log("\n🌟 すべての MP3 と sounds.json のアップロード完了")
        browser.close()

if __name__ == "__main__":
    main()
