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
        prefs = {
            'download.default_directory': str(path),
            'download.prompt_for_download': False,
            'download.directory_upgrade': True,
            'safebrowsing.enabled': True,
        }
        options.add_experimental_option('prefs', prefs)

    os.environ['WDM_LOCAL'] = '1'

    chrome_service = Service(ChromeDriverManager().install())
    browser = Chrome(service=chrome_service, options=options)
    browser.get(url)
    return browser


def download_file(url: str, path: Path = None) -> None:
    browser = None

    while not browser:
        try:
            browser = get_browser(url, path)
        except Exception:
            browser = None

    sleep(3)
    browser.find_element(By.ID, 'download').click()
    sleep(30)
    browser.quit()


def normalize_name(name: str) -> str:
    normalized = (
        normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
    )
    return normalized.strip()


def has_name_in_file(name: str, filename: str) -> Tuple[bool, int]:
    path = Path(OUTPUT_DIR, filename)
    reader = PdfReader(path)
    pattern = re.compile(normalize_name(name), re.MULTILINE | re.IGNORECASE)

    current_page = 1
    for page in reader.pages:
        text = page.extract_text()
        if pattern.search(text):
            return True, current_page
        current_page += 1

    return False, 0


def rename_file(filename: str) -> None:
    path = Path(OUTPUT_DIR, filename)
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


# OUTPUT_DIR = Path(Path.home(), 'Downloads', 'tjce')
# OUTPUT_DIR = Path() / 'files'
OUTPUT_DIR = Path()
BASE_URL = 'https://esaj.tjce.jus.br/cdje/index.do'

names = [
    'PEDRO IVO FREIRE ARAGAO',
    'DANNIEL ALBUQUERQUE ARAUJO',
]

if __name__ == '__main__':
    load_dotenv(find_dotenv())
    download_file(BASE_URL, OUTPUT_DIR)

    today = datetime.strftime(datetime.now(), '%d/%m/%Y')
    pdfs = [file for file in os.listdir(OUTPUT_DIR) if file.endswith('.pdf')]

    for pdf in pdfs:
        name_found = False
        message = ''
        messageToEmail = ''

        for name in names:
            has_name, page_number = has_name_in_file(name, pdf)

            if has_name:
                name_found = True
                message += f'O nome {name} foi encontrado no arquivo {pdf}, na página {page_number} e no dia {today}\n'
                messageToEmail += f'<p>O nome {name} foi encontrado no arquivo {pdf}, na página {page_number} e no dia {today}</p>'

        if name_found:
            print(message)
            try:
                send_email(messageToEmail)
            except Exception:
                print(
                    'Não foi possível enviar o e-mail, verifique se existe o arquivo .env e se SENHA_EMAIL está correta.'
                )
        else:
            print(f'Infelizmente nenhum nome foi encontrado no arquivo {pdf}')

        file = Path(OUTPUT_DIR, pdf)
        os.remove(file)
