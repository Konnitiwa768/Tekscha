import os
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

# ===== 設定 =====
USERNAME = os.getenv("PUP_USER", "example@example.com")
PASSWORD = os.getenv("PUP_PASS", "password123")

# ===== アップロード対象ディレクトリ =====
UPLOAD_DIRS = [
    Path("src/hachiwari_1"),
    Path("src/hachiwari_2"),
    Path("src/marumaru_1"),
    Path("src/marumaru_2"),
    Path("src/kani_1"),
    Path("src/kani_2"),
]

# PowerUpStack 上のアップロード先
TARGET_PATH = "resource_packs%2FRP%2Ftextures%2Fmodels%2Farmor"

SCREENSHOT_DIR = Path("screenshots")
SCREENSHOT_DIR.mkdir(exist_ok=True)

def log(msg: str):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}")

def find_upload_target(page):
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
            el = page.query_selector(sel)
        except Exception as e:
            log(f"⚠️ セレクタ評価エラー ({sel}): {e}")
            continue
        if not el:
            continue

        try:
            tag = el.evaluate("e => e.tagName.toLowerCase()")
        except Exception:
            tag = ""
        typ = (el.get_attribute("type") or "").lower()
        log(f"🔎 セレクタ一致: {sel} -> tag={tag} type={typ}")

        if tag == "input" and typ == "file":
            return el

        try:
            el.click(timeout=2000)
            log(f"✳️ クリックしました: {sel}")
            page.wait_for_timeout(800)
            file_input = page.query_selector('input[type="file"]')
            if file_input:
                log("✅ クリックで input[type=file] を発見")
                return file_input
        except Exception as e:
            log(f"⚠️ クリックしても反応なし: {e}")
        return el

    try:
        fallback = page.query_selector('input[type="file"]')
        if fallback:
            log("✅ フォールバックで input[type=file] を発見")
        return fallback
    except Exception as e:
        log(f"⚠️ フォールバックの検索でエラー: {e}")
        return None

def upload_one(page, path: Path):
    log(f"📤 アップロード開始: {path}")
    try:
        input_box = find_upload_target(page)

        if not input_box:
            log("⚠️ アップロード入力が見つからないのでリロードを試みます")
            page.reload()
            page.wait_for_load_state("networkidle")
            input_box = find_upload_target(page)

        if not input_box:
            log("❌ アップロード入力が見つかりません。スキップ")
            return False

        typ = (input_box.get_attribute("type") or "").lower()
        if typ == "file":
            input_box.set_input_files(str(path))
        else:
            try:
                page.set_input_files('input[type="file"]', str(path))
                log("✅ ページレベルで input[type=file] にファイルをセットしました")
            except Exception as e:
                log(f"⚠️ ページレベルの set_input_files に失敗: {e}")
                try:
                    input_box.set_input_files(str(path))
                except Exception as e2:
                    log(f"❌ 要素ハンドルへの set_input_files に失敗: {e2}")
                    return False

        log(f"✅ ファイル送信済み: {path.name}")
        time.sleep(6)
        shot_name = f"{int(time.time())}_{path.name}.png"
        page.screenshot(path=SCREENSHOT_DIR / shot_name)
        return True
    except Exception as e:
        log(f"⚠️ アップロードエラー: {e}")
        return False

def main():
    # 対象ファイル収集（6ディレクトリ）
    files = []
    for d in UPLOAD_DIRS:
        if not d.exists():
            log(f"⚠️ ディレクトリが存在しません: {d}")
            continue
        for f in sorted(d.glob("*")):
            if f.is_file():
                files.append(f)

    if not files:
        log("❌ アップロード対象のファイルが見つかりません。UPLOAD_DIRS を確認してください。")
        return

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context()
        page = context.new_page()

        log("🌐 PowerUpStack ログインページにアクセス")
        page.goto(
            f"https://www.powerupstack.com/auth/login?redirect=/panel/instances/komugi5/files?path={TARGET_PATH}"
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
