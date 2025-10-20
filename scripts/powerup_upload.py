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

options = webdriver.ChromeOptions()
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)
driver.get("https://www.powerupstack.com/auth/login?redirect=/panel/instances/komugi/files?path=resource_packs")

wait = WebDriverWait(driver, 20)

# === URLログ平行スレッド ===
def log_url_continuously():
    try:
        while True:
            print(f"[LOG] Current URL: {driver.current_url}")
            time.sleep(5)
    except:
        pass

log_thread = threading.Thread(target=log_url_continuously, daemon=True)
log_thread.start()

# === JS root配下の input を待って取得 ===
def wait_for_inputs():
    for _ in range(20):  # 最大20回リトライ
        inputs = driver.execute_script("return document.querySelectorAll('div#root input');")
        if inputs and len(inputs) >= 2:
            return inputs
        time.sleep(0.5)
    raise Exception("Input fields not found in root")

inputs = wait_for_inputs()

# Selenium WebElement に変換（execute_script だとJSオブジェクトなので）
inputs[0].send_keys(USERNAME)
inputs[1].send_keys(PASSWORD)

# loginボタンも root 内で取得
login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='root']//button[contains(., 'login') or contains(., 'Login')]")))
login_button.click()

# ページ遷移を JS root に合わせて固定待機
time.sleep(15)

# upload ボタン取得
upload_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='root']//button[contains(., 'upload') or contains(., 'Upload files')]")))
upload_button.click()

# input[type=file] に Pack/ を指定
file_input = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='root']//input[@type='file']")))
file_input.send_keys(FILE_PATH)

print("✅ Upload Completed")
print(f"[LOG] Final URL: {driver.current_url}")

time.sleep(3)
driver.quit()
