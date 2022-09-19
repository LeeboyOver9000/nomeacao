import email.message
import os
import smtplib
import re

from datetime import datetime
from pathlib import Path
from time import sleep
from typing import Tuple
from unicodedata import normalize

from PyPDF2 import PdfReader
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

def normalize_name(name: str) -> str:
    normalized = (
        normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
    )
    return normalized.strip()


def has_name_in_file(name: str, path: str) -> Tuple[bool, int]:
    reader = PdfReader(path)
    pattern = re.compile(normalize_name(name), re.IGNORECASE)

    current_page = 1
    for page in reader.pages:
        text = page.extract_text()
        if re.search(pattern, text):
            return True, current_page
        current_page += 1

    return False, 0

def get_browser(url: str, path: Path = None) -> WebDriver:
    options = Options()
    options.add_argument('--headless')
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-gpu')
    options.add_argument('--disable-infobars')
    options.add_argument('--disable-extensions')
    options.add_argument('--dns-prefetch-disable')

    if path:
        path.mkdir(exist_ok=True)
        prefs = {'download.default_directory': f'{path}'}
        options.add_experimental_option('prefs', prefs)

    chrome_service = Service(ChromeDriverManager().install())
    browser = Chrome(service=chrome_service, options=options)
    browser.get(url)
    return browser


def download_file(url: str, path: Path = None) -> None:
    browser = get_browser(url, path)
    sleep(3)
    browser.find_element(By.ID, 'download').click()
    sleep(15)
    browser.quit()

def rename_file(output_path: Path, filename: str = None) -> None:
    path = Path(output_path, filename) if filename is not None else Path(output_path)
    if path.is_file():
        old_name = path.stem.split('-')[0]
        today = datetime.strftime(datetime.now(), '%d-%m-%Y')
        new_name = f'{old_name}-{today}.pdf'
        path.rename(Path(path.parent, new_name))


def send_email(message: str) -> None:
    corpo_email = f"""
    <h1>Nomeação no Diário da Justíça</h1>
    {message}
    """

    msg = email.message.Message()
    msg['Subject'] = 'Nomeação TJ CE'
    msg['From'] = 'pedro.ivo.freire.aragao@gmail.com'
    msg['To'] = 'pedro.ivo.freire.aragao@gmail.com'
    password = os.environ.get('SENHA_EMAIL')
    msg.add_header('Content-Type', 'text/html')
    msg.set_payload(corpo_email)

    server = smtplib.SMTP('smtp.gmail.com: 587')
    server.starttls()
    server.login(msg['From'], password)
    server.sendmail(msg['From'], [msg['To']], msg.as_string().encode('utf-8'))
