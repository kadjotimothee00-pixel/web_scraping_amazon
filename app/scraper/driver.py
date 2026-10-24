"""Création et configuration du navigateur Chrome piloté par Selenium."""
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

import config


def create_driver() -> webdriver.Chrome:
    options = Options()
    if config.HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1366,768")
    options.add_argument("--disable-notifications")
    options.add_argument("--lang=fr-FR")
    # Selenium 4 télécharge automatiquement le bon chromedriver (Selenium Manager)
    return webdriver.Chrome(options=options)
