from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import threading

USERNAME = os.getenv("PUP_USER")
PASSWORD = os.getenv("PUP_PASS")
FILE_PATH = "Pack/"
SCREENSHOT_DIR = "screenshots"

os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def save_screenshot(driver, name):
    """ステップごとに固定名で上書き保存"""
    path = os.path.join(SCREENSHOT_DIR, f"{name}.png")
    driver.save_screenshot(path)
    print(f"[📸] Saved: {path}")

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("--window-size=1280,800")

driver = webdriver.Chrome(options=options)
wait = WebDriverWait(driver, 20)

driver.get("https://www.powerupstack.com/auth/login?redirect=/panel/instances/komugi/files?path=resource_packs")
save_screenshot(driver, "01_login_page")

# === URLログスレッド ===
def log_urls():
    try:
        while True:
            print(f"[LOG] Current URL: {driver.current_url}")
            time.sleep(5)
    except:
        pass

threading.Thread(target=log_urls, daemon=True).start()

# === Email/Password入力 ===
def find_input_by_label(label_text):
    for _ in range(20):
        labels = driver.find_elements(By.TAG_NAME, "label")
        for lbl in labels:
            if lbl.text.strip() == label_text:
                input_id = lbl.get_attribute("for")
                if input_id:
                    return driver.find_element(By.ID, input_id)
        time.sleep(0.5)
    raise Exception(f"Label '{label_text}' not found")

email_input = find_input_by_label("Email")
password_input = find_input_by_label("Password")
save_screenshot(driver, "02_found_inputs")

email_input.clear()
email_input.send_keys(USERNAME)
password_input.clear()
password_input.send_keys(PASSWORD)
save_screenshot(driver, "03_filled_credentials")

# === ログインボタン ===
login_button = wait.until(
    EC.element_to_be_clickable((By.XPATH, "//div[@id='root']//button[contains(., 'login') or contains(., 'Login')]"))
)
login_button.click()
time.sleep(5)
save_screenshot(driver, "04_after_login")

# === ファイルページに移動 ===
driver.get("https://www.powerupstack.com/panel/instances/komugi/files?path=resource_packs")
time.sleep(6)
save_screenshot(driver, "05_resource_page")

# === Uploadボタン ===
upload_button = wait.until(
    EC.element_to_be_clickable((By.XPATH, "//div[@id='root']//button[contains(., 'upload') or contains(., 'Upload files')]"))
)
upload_button.click()
save_screenshot(driver, "06_clicked_upload")

# === ファイル送信 ===
file_input = wait.until(
    EC.presence_of_element_located((By.XPATH, "//div[@id='root']//input[@type='file']"))
)
file_input.send_keys(FILE_PATH)
save_screenshot(driver, "07_file_sent")

print("✅ Upload Completed")
print(f"[LOG] Final URL: {driver.current_url}")

time.sleep(3)
driver.quit()
