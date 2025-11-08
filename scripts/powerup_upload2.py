import os
import time
from pathlib import Path
import json
from playwright.sync_api import sync_playwright

# ===== 設定 =====
USERNAME = os.getenv("PUP_USER", "example@example.com")
PASSWORD = os.getenv("PUP_PASS", "password123")

UPLOAD_DIR = Path("resource_packs/RP/sounds")
SCREENSHOT_DIR = Path("screenshots")
SCREENSHOT_DIR.mkdir(exist_ok=True)

# MP3 ファイル一覧
files = sorted(UPLOAD_DIR.glob("*.mp3"))

# sounds.json のパス
sounds_json_path = UPLOAD_DIR.parent / "sounds.json"

def log(msg: str):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")

def generate_sounds_json():
    sounds = {}
    for mp3_path in files:
        name = mp3_path.stem  # 例: phyle_idle
        sounds[name] = {"sounds": [f"myaddon:{name}"]}
    with open(sounds_json_path, "w", encoding="utf-8") as f:
        json.dump(sounds, f, ensure_ascii=False)
    log(f"✔ sounds.json を生成: {sounds_json_path}")
    return sounds_json_path

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
        time.sleep(6)
        page.screenshot(path=SCREENSHOT_DIR / f"{path.name}.png")
        return True
    except Exception as e:
        log(f"⚠️ アップロードエラー: {e}")
        return False

def main():
    if not files:
        log("❌ アップロード対象の MP3 がありません")
        return

    # sounds.json 生成
    generate_sounds_json()

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        log("🌐 PowerUpStack ログインページにアクセス")
        page.goto("https://www.powerupstack.com/auth/login?redirect=/panel/instances/komugi5/files?path=resource_packs/RP/sounds")
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

        # MP3 ファイル逐次アップロード
        for i, file_path in enumerate(files, start=1):
            log(f"\n===== ステップ {i}/{len(files)} =====")
            ok = upload_one(page, file_path)
            if ok:
                log(f"🎉 {file_path.name} のアップロード完了")
            else:
                log(f"⚠️ {file_path.name} のアップロードに失敗")
            time.sleep(3)

        # sounds.json アップロード
        log("\n===== sounds.json アップロード =====")
        upload_one(page, sounds_json_path)

        log("\n🌟 すべての MP3 と sounds.json のアップロード完了")
        browser.close()

if __name__ == "__main__":
    main()
