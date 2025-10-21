from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import threading
import traceback

USERNAME = os.getenv("PUP_USER", "example@example.com")
PASSWORD = os.getenv("PUP_PASS", "password123")
FILE_PATH = "Pack/"
SCREENSHOT_DIR = "screenshots"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def safe_action(step_name, func):
    """例外を握りつぶして続行"""
    try:
        print(f"[STEP] {step_name}")
        func()
        print(f"✅ {step_name} 完了")
    except Exception as e:
        print(f"[⚠️] {step_name} でエラー: {e}")
        traceback.print_exc()

def save_screenshot(driver, name):
    """ステップごとに固定名で上書き保存"""
    try:
        path = os.path.join(SCREENSHOT_DIR, f"{name}.png")
        driver.save_screenshot(path)
        print(f"[📸] Saved: {path}")
    except:
        pass

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1280,800")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 20)

# === URLログスレッド ===
def log_urls():
    try:
        while True:
            print(f"[LOG] Current URL: {driver.current_url}")
            time.sleep(5)
    except Exception:
        pass

threading.Thread(target=log_urls, daemon=True).start()

# === ステップ1: ログインページへ ===
safe_action("ログインページへ移動", lambda: driver.get(
    "https://www.powerupstack.com/auth/login?redirect=/panel/instances/komugi/files?path=resource_packs"
))
save_screenshot(driver, "01_login_page")

# === ステップ2: 入力欄を取得して入力 ===
def input_credentials():
    inputs = driver.find_elements(By.TAG_NAME, "input")
    if len(inputs) >= 2:
        inputs[0].clear()
        inputs[0].send_keys(USERNAME)
        inputs[1].clear()
        inputs[1].send_keys(PASSWORD)
    else:
        raise Exception("入力欄が2つ未満です")

safe_action("認証情報入力", input_credentials)
save_screenshot(driver, "02_filled_credentials")

# === ステップ3: ログインボタンをクリック ===
def click_login():
    btn = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(translate(., 'LOGIN', 'login'), 'login')]")
        )
    )
    btn.click()
    time.sleep(5)

safe_action("ログインボタン押下", click_login)
save_screenshot(driver, "03_after_login")

# === ステップ4: ファイルページに遷移 ===
safe_action("ファイルページへ移動", lambda: driver.get(
    "https://www.powerupstack.com/panel/instances/komugi/files?path=resource_packs"
))
time.sleep(6)
save_screenshot(driver, "04_resource_page")

# === ステップ5: アップロードボタン押下 ===
def click_upload_button():
    btn = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//button[contains(translate(., 'UPLOAD', 'upload'), 'upload')]")
        )
    )
    btn.click()
    time.sleep(2)

safe_action("アップロードボタン押下", click_upload_button)
save_screenshot(driver, "05_clicked_upload")

# === ステップ6: ファイル送信 ===
def send_file():
    file_input = wait.until(
        EC.presence_of_element_located((By.XPATH, "//input[@type='file']"))
    )
    file_input.send_keys(FILE_PATH)
    time.sleep(2)

safe_action("ファイル送信", send_file)
save_screenshot(driver, "06_file_sent")

print("✅ 全ステップ完了（エラー無視モード）")
print(f"[LOG] Final URL: {driver.current_url}")

time.sleep(3)
driver.quit()
