import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By

BASE_URL = "http://localhost:5000"
ADMIN_USERNAME = "admin"


def get_admin_password():
    # El bot necesita loguearse como admin; la contrasena real es aleatoria
    # y solo la conoce el propio servidor (se genera en init_db). Por eso el
    # bot la obtiene mediante un endpoint interno de arranque, no por fuerza bruta.
    resp = requests.get(f"{BASE_URL}/internal/_bot_credentials", timeout=10)
    resp.raise_for_status()
    return resp.json()["password"]


def build_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.add_argument("--window-size=1280,800")
    service = Service("/usr/bin/chromedriver")
    return webdriver.Chrome(service=service, options=options)


def wait_for_app():
    for _ in range(60):
        try:
            r = requests.get(BASE_URL, timeout=3)
            if r.status_code in (200, 302):
                return True
        except Exception:
            pass
        time.sleep(2)
    return False


def login_as_admin(driver, password):
    driver.get(f"{BASE_URL}/login")
    time.sleep(1)
    driver.find_element(By.NAME, "username").send_keys(ADMIN_USERNAME)
    driver.find_element(By.NAME, "password").send_keys(password)
    driver.find_element(By.TAG_NAME, "form").submit()
    time.sleep(1)


def main():
    if not wait_for_app():
        print("[bot] la aplicacion no respondio, abortando bot")
        return

    password = get_admin_password()
    driver = build_driver()
    login_as_admin(driver, password)
    print("[bot] admin autenticado, iniciando revision periodica de pedidos")

    last_seen = None
    while True:
        try:
            r = requests.get(f"{BASE_URL}/internal/latest_id", timeout=5)
            latest_id = r.json().get("id")
            if latest_id and latest_id != last_seen:
                print(f"[bot] revisando comprobante nuevo #{latest_id}")
                driver.get(f"{BASE_URL}/voucher/{latest_id}")
                time.sleep(2)
                last_seen = latest_id
        except Exception as e:
            print(f"[bot] error en ciclo: {e}")
        time.sleep(10)


if __name__ == "__main__":
    main()
