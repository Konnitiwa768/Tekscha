# GitHub Copilot Chat Assistant
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

def find_upload_target(page):
    """ページ上でアップロード用のターゲット（できれば input[type=file]）を探す。
    指定された順序でセレクタを試し、見つかった要素が file input であればそれを返す。
    ボタンや他の要素が見つかった場合はクリックして隠し input[type=file] を表示させることを試みる。
    最後に通常の input[type=file] を直接検索して返す。
    """
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
            # セレクタが無効な場合や評価でエラーが起きた場合はスキップ
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

        # 見つかった要素が file input ならそのまま返す
        if tag == "input" and typ == "file":
            return el

        # 非 file 要素だったらクリックして隠し input が出てくるか試す
        try:
            el.click(timeout=2000)
            log(f"✳️ クリックしました: {sel}")
            # クリック後に input[type=file] が出てくることを期待して短く待つ
            page.wait_for_timeout(800)
            file_input = page.query_selector('input[type="file"]')
            if file_input:
                log("✅ クリックで input[type=file] を発見")
                return file_input
        except Exception as e:
            log(f"⚠️ クリックしても反応なし: {e}")

        # 最後の手段として、その要素自体を返す（場合によっては element_handle.set_input_files が使える）
        return el

    # 総当たりで見つからなかった場合は通常の file input を直接探す
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

        # 要素が input[type=file] なら直接 set_input_files を使う
        typ = (input_box.get_attribute("type") or "").lower()
        if typ == "file":
            input_box.set_input_files(str(path))
        else:
            # 要素が file input でない場合、一旦ページレベルで試す
            try:
                page.set_input_files('input[type="file"]', str(path))
                log("✅ ページレベルで input[type=file] にファイルをセットしました")
            except Exception as e:
                log(f"⚠️ ページレベルの set_input_files に失敗: {e}")
                # 最後に要素ハンドルで試す（失敗する可能性あり）
                try:
                    input_box.set_input_files(str(path))
                except Exception as e2:
                    log(f"❌ 要素ハンドルへの set_input_files に失敗: {e2}")
                    return False

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
    mp3_files = sorted(SOUNDS_DIR.glob("*.ogg"))
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
            if len(inputs) >= 2:
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
