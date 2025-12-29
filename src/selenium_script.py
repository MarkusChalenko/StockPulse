from asyncio import sleep
from dataclasses import dataclass

from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

from src.core.broker import RedisPubSub
from src.core.config import get_settings


@dataclass
class CookiesData:
    navi_token: str
    gwSessionID: str
    psid: str


async def get_cookies_from_t() -> CookiesData:
    options = Options()
    driver = webdriver.Chrome(service=Service(), options=options)

    try:
        # Главная страница
        driver.get(get_settings().MAIN_URL)
        await sleep(1)

        # Отображаем выпадающее меню "Личный кабинет"
        menu_button = driver.find_element(By.CSS_SELECTOR, 'span[data-test="loginButton"]')
        ActionChains(driver).move_to_element(menu_button).perform()

        await sleep(1)

        # Нажимаем на кнопку "Т-Инвестиции" в выпадающем меню (3 элемент)
        redirect_btn = driver.find_element(By.CSS_SELECTOR, 'li[data-schema-path="third"]')
        redirect_btn.click()

        await sleep(1)

        # Переключаем таргет на новое окно
        windows = driver.window_handles
        driver.switch_to.window(windows[-1])

        await sleep(1)

        # Вводим мобильный телефон
        phone_input = driver.find_element(By.CSS_SELECTOR, 'input[automation-id="phone-input"]')
        phone_input.send_keys(get_settings().PHONE_NUMBER)

        await sleep(1)

        # жмём "Продолжить"
        next_btn = driver.find_element(By.CSS_SELECTOR,
                                       'button[automation-id="button-submit"]')  # тут лучше уточнить селектор под конкретную кнопку
        next_btn.click()

        # 3. ждем появления формы для ввода кода
        # print("Введи SMS-код вручную в открытом браузере...")
        # code = input("Когда введёшь код и попадёшь в личный кабинет, нажми Enter здесь >>> ")

        otp_code: str
        async with RedisPubSub() as broker:
            await broker.subscribe("otp_code")
            otp_code = await broker.get_message()

        code_input = driver.find_element(By.CSS_SELECTOR, 'input[automation-id="otp-input"]')
        code_input.send_keys(otp_code)

        await sleep(3)

        # Отказываемся от установки кода для входа
        cancel_btn = driver.find_element(By.CSS_SELECTOR,
                                         'button[automation-id="cancel-button"]')
        cancel_btn.click()

        await sleep(10)

        # берём куки
        cookies = driver.get_cookies()
        navi_token = gwSessionID = psid = ""
        for c in cookies:
            if c["name"] == "navi_token":
                navi_token = c["value"]
            if c["name"] == "gwSessionID":
                gwSessionID = c["value"]
            if c["name"] == "psid":
                psid = c["value"]
        return CookiesData(navi_token, gwSessionID, psid)
    finally:
        driver.quit()
