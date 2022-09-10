import re
from typing import Tuple
from unicodedata import normalize
from PyPDF2 import PdfReader

def normalize_name(name: str) -> str:
    normalized = (
        normalize('NFKD', name).encode('ASCII', 'ignore').decode('ASCII')
    )
    return normalized.strip().upper()


def has_name_in_file(name: str, path: str) -> Tuple[bool, int]:
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
