import os
import time
import asyncio
from playwright.async_api import async_playwright

USERNAME = os.getenv("PUP_USER", "example@example.com")
PASSWORD = os.getenv("PUP_PASS", "password123")
FILE_PATH = "Pack/"  # アップロード対象
SCREENSHOT_DIR = "screenshots"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        # === ステップ1: ログインページへ ===
        print("[STEP] ログインページへ移動")
        await page.goto("https://www.powerupstack.com/auth/login?redirect=/panel/instances/komugi/files?path=resource_packs")
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "01_login_page.png"))

        # === ステップ2: 認証情報入力 ===
        print("[STEP] 認証情報入力")
        await page.fill("input[type='email']", USERNAME)
        await page.fill("input[type='password']", PASSWORD)
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "02_filled_credentials.png"))

        # === ステップ3: ログインボタン ===
        print("[STEP] ログインボタン押下")
        await page.click("button:has-text('Login')")
        await page.wait_for_load_state("networkidle")
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "03_after_login.png"))

        # === ステップ4: ファイルページ ===
        print("[STEP] ファイルページへ移動")
        await page.goto("https://www.powerupstack.com/panel/instances/komugi/files?path=resource_packs")
        await page.wait_for_load_state("networkidle")
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "04_resource_page.png"))

        # === ステップ5: アップロードボタン ===
        print("[STEP] アップロードボタン押下")
        await page.click("button:has-text('Upload')")
        await asyncio.sleep(1)
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "05_clicked_upload.png"))

        # === ステップ6: ファイル送信 ===
        print("[STEP] ファイル送信")
        # Playwrightのfile chooserイベントで送信
        async with page.expect_file_chooser() as fc_info:
            await page.click("input[type='file'], button:has-text('Choose File')")
        file_chooser = await fc_info.value
        await file_chooser.set_files(FILE_PATH)
        await asyncio.sleep(2)
        await page.screenshot(path=os.path.join(SCREENSHOT_DIR, "06_file_sent.png"))

        print("✅ 全ステップ完了")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
