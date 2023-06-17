import requests

import fitz

import concurrent.futures

import asyncio

import httpx


def download_pdf_from_url(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        raise Exception(f"Не удалось скачать PDF по URL: {url}")


async def download_pdf_from_url_async(url):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
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


async def convert_pdf_to_text_async(pdf_content):
    loop = asyncio.get_running_loop()
    with concurrent.futures.ThreadPoolExecutor() as executor:
        text = await loop.run_in_executor(executor, convert_pdf_to_text, pdf_content)

    return text


def process_url(url):
    pdf_content = download_pdf_from_url(url)
    pdf_text = convert_pdf_to_text(pdf_content)

    return pdf_text


async def process_url_async(url):
    pdf_content = await download_pdf_from_url_async(url)
    pdf_text = await convert_pdf_to_text_async(pdf_content)

    return pdf_text
