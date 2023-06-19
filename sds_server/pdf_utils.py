import requests

import fitz


def download_pdf_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"Не удалось скачать PDF по URL: {url}")


def convert_pdf_to_text(pdf_content):
    doc = fitz.open("pdf", pdf_content)
    text = ""
    for page in doc:
        text += page.get_text()

    return text


def process_url(url):
    pdf_content = download_pdf_from_url(url)
    pdf_text = convert_pdf_to_text(pdf_content)

    return pdf_text
