import os
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

# ===== 設定 =====
USERNAME = os.getenv("PUP_USER", "example@example.com")
PASSWORD = os.getenv("PUP_PASS", "password123")

# ===== アップロード対象ファイル =====
FILES = [
    Path("src/hachiwari_1.png"),
    Path("src/hachiwari_2.png"),
    Path("src/marumaru_1.png"),
    Path("src/marumaru_2.png"),
    Path("src/kani_1.png"),
    Path("src/kani_2.png"),
]

# ===== アップロード先 =====
TARGET_URL = (
    "https://www.powerupstack.com/auth/login"
    "?redirect=/panel/instances/komugi5/files?path=resource_packs%2FRP%2Ftextures%2Fmodels%2Farmor"
)

SCREENSHOT_DIR = Path("screenshots")
SCREENSHOT_DIR.mkdir(exist_ok=True)

def log(msg: str):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")

def find_upload_target(page):
    selectors = [
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
            el = page.query_selector(sel)
            if el:
                tag = el.evaluate("e => e.tagName.toLowerCase()")
                typ = (el.get_attribute("type") or "").lower()
                log(f"🔎 検出: {sel} tag={tag} type={typ}")
                if tag == "input" and typ == "file":
                    return el
                el.click(timeout=2000)
                page.wait_for_timeout(800)
                file_input = page.query_selector('input[type="file"]')
                if file_input:
                    log("✅ input[type=file] を発見")
                    return file_input
        except Exception as e:
            log(f"⚠️ 検索エラー: {e}")
    return None

def upload_one(page, path: Path):
    log(f"📤 アップロード開始: {path}")
    if not path.exists():
        log(f"❌ ファイルが存在しません: {path}")
        return False
    try:
        input_box = find_upload_target(page)
        if not input_box:
            log("⚠️ input[type=file] が見つからずリロード中")
            page.reload()
            page.wait_for_load_state("networkidle")
            input_box = find_upload_target(page)
        if not input_box:
            log("❌ アップロード要素が見つかりません")
            return False

        input_box.set_input_files(str(path))
        log(f"✅ ファイル送信済み: {path.name}")
        time.sleep(6)
        shot_name = f"{int(time.time())}_{path.name}.png"
        page.screenshot(path=SCREENSHOT_DIR / shot_name)
        return True
    except Exception as e:
        log(f"⚠️ アップロードエラー: {e}")
        return False

def main():
    files = [f for f in FILES if f.exists()]
    if not files:
        log("❌ アップロード対象のファイルが見つかりません。")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        log("🌐 PowerUpStack ログインページにアクセス")
        page.goto(TARGET_URL)
        page.wait_for_load_state("networkidle")

        inputs = page.query_selector_all("input")
        if len(inputs) >= 2:
            inputs[0].fill(USERNAME)
            inputs[1].fill(PASSWORD)
        login_btn = page.query_selector("button:has-text('Login')")
        if login_btn:
            login_btn.click()
        else:
            if len(inputs) >= 2:
                inputs[1].press("Enter")

        page.wait_for_load_state("networkidle")
        log("✔ ログイン完了")
        page.screenshot(path=SCREENSHOT_DIR / "login_done.png")

        for i, file_path in enumerate(files, start=1):
            log(f"\n===== ステップ {i}/{len(files)} =====")
            ok = upload_one(page, file_path)
            if ok:
                log(f"🎉 {file_path.name} のアップロード完了")
            else:
                log(f"⚠️ {file_path.name} のアップロードに失敗")
            time.sleep(3)

        log("\n🌟 すべてのファイルアップロード完了")
        browser.close()

if __name__ == "__main__":
    main()
