from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time

# === Secretsから取得 ===
USERNAME = os.getenv("PUP_USER")
PASSWORD = os.getenv("PUP_PASS")
FILE_PATH = "Pack/"  # リポジトリ内パスまたは絶対パス

# === Headless Chrome設定 ===
options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)
driver.get("https://www.powerupstack.com/auth/login?redirect=/panel/instances/komugi/files?path=resource_packs")

wait = WebDriverWait(driver, 20)

# === ログイン入力 ===
field0 = wait.until(EC.presence_of_element_located((By.ID, "0")))
field1 = wait.until(EC.presence_of_element_located((By.ID, "1")))

field0.clear()
field0.send_keys(USERNAME)

field1.clear()
field1.send_keys(PASSWORD)

login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'login') or contains(., 'Login')]")))
login_button.click()

# === ページ遷移待ち ===
wait.until(EC.url_contains("/panel/instances/komugi/files"))

# === uploadボタン探してクリック ===
upload_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'upload') or contains(., 'Upload')]")))
upload_button.click()

# === input[type=file] に Pack/ を指定 ===
file_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))
file_input.send_keys(FILE_PATH)

print("✅ PowerUpStack: Upload Completed")

time.sleep(3)
driver.quit()
