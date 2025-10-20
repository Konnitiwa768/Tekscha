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

# 平行ログスレッド
def log_url_continuously():
    try:
        while True:
            print(f"[LOG] Current URL: {driver.current_url}")
            time.sleep(5)
    except:
        pass

log_thread = threading.Thread(target=log_url_continuously, daemon=True)
log_thread.start()

# === Email / Password ラベルに紐づく input を JS で取得 ===
def find_input_by_label(label_text):
    script = f"""
    const labels = document.querySelectorAll('label');
    for (let lbl of labels) {{
        if (lbl.textContent.trim() === "{label_text}") {{
            const id = lbl.getAttribute('for');
            if (id) return document.getElementById(id);
        }}
    }}
    return null;
    for _ in range(20):  # 最大20回リトライ
        input_elem = driver.execute_script(script)
        if input_elem:
            return input_elem
        time.sleep(0.5)
    raise Exception(f"Input field with label '{label_text}' not found")

email_input = find_input_by_label("Email")
password_input = find_input_by_label("Password")

email_input.send_keys(USERNAME)
password_input.send_keys(PASSWORD)

# loginボタン
login_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@id='root']//button[contains(., 'login') or contains(., 'Login')]")))
login_button.click()

# ログイン後ページを直接開く
driver.get("https://www.powerupstack.com/panel/instances/komugi/files?path=resource_packs")
time.sleep(6)

# uploadボタン操作
upload_button = wait.until(EC.element_to_be_clickable(
    (By.XPATH, "//div[@id='root']//button[contains(., 'upload') or contains(., 'Upload files')]")
))
upload_button.click()

# ファイル送信
file_input = wait.until(EC.presence_of_element_located((By.XPATH, "//div[@id='root']//input[@type='file']")))
file_input.send_keys(FILE_PATH)

print("✅ Upload Completed")
print(f"[LOG] Final URL: {driver.current_url}")

time.sleep(3)
driver.quit()
