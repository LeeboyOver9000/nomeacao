import email.message
import os
import smtplib
import re
from pathlib import Path
from time import sleep
from typing import Tuple
from unicodedata import normalize
from datetime import datetime

from dotenv import load_dotenv, find_dotenv

from PyPDF2 import PdfReader
from selenium.webdriver import Chrome
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager


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


def normalize_name(name: str) -> str:
    normalized = (
        normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
    )
    return normalized.strip().upper()


def has_name_in_file(name: str, filename: str) -> Tuple[bool, int]:
    path = Path(OUTPUT_DIR, filename)
    reader = PdfReader(path)
    # name_normalized = normalize_name(name)
    pattern = re.compile(name.strip(), re.IGNORECASE)

    current_page = 1
    for page in reader.pages:
        text = page.extract_text()
        # if name_normalized in text:
        if re.search(pattern, text):
            return True, current_page
        current_page += 1

    return False, 0


def rename_file(filename: str) -> str:
    path = Path(OUTPUT_DIR, filename)
    old_name = path.stem.split('-')[0]
    today = datetime.strftime(datetime.now(), '%d-%m-%Y')
    new_name = f'{old_name}-{today}.pdf'
    path.rename(Path(path.parent, new_name))
    return new_name


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


OUTPUT_DIR = Path(Path.home(), 'Downloads')
BASE_URL = 'https://esaj.tjce.jus.br/cdje/index.do'

names = [
    'PEDRO IVO FREIRE ARAGAO',
    'EWERTON ALMEIDA SILVA',
    'WENDELL MILITAO FERNANDES MENDES',
    'ANTONIO LUIS SOMBRA DE MEDEIROS',
    'ABELARDO VIEIRA MOTA',
    'FABIANO JOSE GADELHA DE FREITAS',
    'LEANDRO HENRIQUE DE SOUZA SANTOS',
    'DOUGLAS PEIXOTO RODRIGUES',
    'ANTONIO GABRIEL DA SILVA FERNANDES',
    'JOAO MARCOS CARVALHO LIMA'
]

if __name__ == '__main__':
    load_dotenv(find_dotenv())
    download_file(BASE_URL, OUTPUT_DIR)

    pdfs = [file for file in os.listdir(OUTPUT_DIR) if file.endswith('.pdf')]

    for pdf in pdfs:
        name_found = False
        message = ''

        for name in names:
            has_name, page_number = has_name_in_file(name, pdf)
            filename = rename_file(pdf)
            if has_name:
                name_found = True
                message += f'<p>Opa! Encontramos o nome {name} no arquivo {filename} na página {page_number}</p>'

        if not name_found:
            file = Path(OUTPUT_DIR, filename)
            os.remove(file)
        else:
            send_email(message)
