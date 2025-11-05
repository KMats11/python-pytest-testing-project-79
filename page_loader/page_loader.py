import logging
import os
import re
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def make_filename(url, extension=None):
    """Генерирует безопасное имя файла на основе URL и расширения (если указано)"""
    parsed = urlparse(url)
    path = parsed.netloc + parsed.path
    # Отделяем расширение заранее
    root, ext_from_path = os.path.splitext(path)
    clean_name = re.sub(r'\W+', '-', root).strip('-')

    # Определяем расширение
    if extension:
        ext = extension
    else:
        ext = ext_from_path.lstrip('.')
        if not ext:
            ext = 'html'

    return f"{clean_name}.{ext}"


def download_resource(resource_url, save_path):
    """Скачивает и сохраняет ресурс"""
    logger.info(f"Скачивание ресурса: {resource_url}")
    response = requests.get(resource_url)

    response.raise_for_status()

    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    with open(save_path, 'wb') as f:
        f.write(response.content)
    logger.info(f"Ресурс сохранён: {save_path}")


def is_local_resource(resource_url, base_url):
    """Проверяет, что ресурс принадлежит тому же хосту"""
    return urlparse(resource_url).netloc in ('', urlparse(base_url).netloc)


def download(url, output_dir=os.getcwd()):
    logger.info(f"Загрузка страницы: {url}")
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, 'html.parser')
    base_name = make_filename(url, 'html').replace('.html', '')
    resource_dir = os.path.join(output_dir, f"{base_name}_files")

    try:
        os.makedirs(resource_dir, exist_ok=True)
    except OSError as e:
        raise Exception(f"Ошибка при создании директории {resource_dir}: {e}") from e

    tags = soup.find_all(['img', 'link', 'script'])
    for tag in tags:
        attr = 'src' if tag.name in ['img', 'script'] else 'href'
        link = tag.get(attr)
        if not link:
            continue

        full_url = urljoin(url, link)
        if not is_local_resource(full_url, url):
            continue

        resource_filename = make_filename(full_url)
        resource_path = os.path.join(resource_dir, resource_filename)

        try:
            logger.info(f"Сохраняем ресурс {full_url} как {resource_path}")

            download_resource(full_url, resource_path)
            tag[attr] = f"{base_name}_files/{resource_filename}"
        except requests.RequestException as e:
            logger.warning(f"Ошибка при скачивании ресурса {full_url}: {e}")

    # Сохраняем изменённый HTML
    html_path = os.path.join(output_dir, f"{base_name}.html")

    try:
        os.makedirs(output_dir, exist_ok=True)
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(soup.prettify())
    except OSError as e:
        raise Exception(f"Ошибка при сохранении HTML-файла {html_path}: {e}") from e

    logger.info(f"HTML сохранён: {html_path}")
    return html_path
