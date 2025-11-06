import logging
import os
import tempfile
from pathlib import Path

import pytest
import requests
import requests_mock
from bs4 import BeautifulSoup

from page_loader.page_loader import make_filename, download

# Настройка логирования для читаемого вывода
logging.basicConfig(level=logging.DEBUG, format="%(levelname)s: %(message)s")
logger = logging.getLogger(__name__)


@pytest.fixture
def temp_dir():
    """Фикстура для создания временной директории"""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname


def test_make_filename():
    """Тестирование создания имени файла из URL"""
    urls = [
        ("https://ru.hexlet.io/courses", "ru-hexlet-io-courses.html"),
        ("http://example.com/path/page", "example-com-path-page.html"),
        ("https://ru.wikipedia.org/wiki/Покрытие_кода", "ru-wikipedia-org-wiki-Покрытие_кода.html"),
    ]

    logger.info("Проверяем генерацию имён файлов из URL")
    for url, expected in urls:
        result = make_filename(url)
        logger.debug(f"{url} -> {result}")
        assert result == expected


@pytest.mark.parametrize("status_code", [404, 500])
def test_response_errors(temp_dir, status_code):
    """Тестирование обработки ошибок 404 и 500"""
    url = f"https://site.com/error-{status_code}"

    with requests_mock.Mocker() as m:
        m.get(url, status_code=status_code)
        logger.info("Проверяем обработку ошибки HTTP %s для %s", status_code, url)

        with pytest.raises(requests.exceptions.HTTPError):
            download(url, temp_dir)
            logger.debug("Ошибка %s корректно вызвала исключение", status_code)


@pytest.mark.parametrize("invalid_path", ["C:\\fake_path"])
def test_storage_errors(invalid_path, monkeypatch):
    """Тестирование ошибки при недоступной директории"""
    url = "https://site.com/blog/about"

    def fake_makedirs(path, exist_ok=False):
        raise PermissionError("Нет доступа")

    monkeypatch.setattr(os, "makedirs", fake_makedirs)
    logger.info("Проверяем поведение при PermissionError")

    with requests_mock.Mocker() as m:
        m.get(url, text="<html></html>")
        with pytest.raises(Exception):
            download(url, invalid_path)
        logger.debug("PermissionError корректно вызвал исключение")


def test_download(temp_dir):
    """Тестирование скачивания страницы"""
    url = "https://ru.hexlet.io/courses"
    test_page_text = "<html><body>Test Page</body></html>"
    expected_filename = os.path.join(temp_dir, "ru-hexlet-io-courses.html")
    expected_html = BeautifulSoup(test_page_text, "html.parser").prettify()

    with requests_mock.Mocker() as m:
        m.get(url, text=test_page_text)  # Подмена запроса
        logger.info("Начинаем тест скачивания страницы %s", url)

        file_path = download(url, temp_dir)
        logger.debug("Файл сохранён по пути: %s", file_path)

        # Проверка, что файл создан и корректен
        assert os.path.exists(file_path)
        assert file_path == expected_filename

        # Проверка содержимого файла
        with open(file_path, encoding="utf-8") as file:
            assert file.read() == expected_html

        # Проверка, что requests.get(url) был вызван ОДИН раз
        assert len(m.request_history) == 1
        # Проверка, что запрос был сделан по нужному URL
        assert m.request_history[0].url == url
        # Проверка, что это именно GET-запрос
        assert m.request_history[0].method == "GET"
        logger.info("Тест скачивания страницы успешно пройден")


def test_download_with_images(tmp_path):
    """Тестирование скачивания изображений и замены ссылок"""
    url = "https://ru.hexlet.io/courses"
    html_content = '''
    <html>
      <body>
        <img src="/assets/professions/python.png" />
      </body>
    </html>
    '''
    img_url = "https://ru.hexlet.io/assets/professions/python.png"
    # Загружаем реальную картинку из fixtures
    real_image_path = Path("tests/fixtures/python.png")
    img_content = real_image_path.read_bytes()

    expected_img_filename = "ru-hexlet-io-assets-professions-python.png"
    expected_img_path = os.path.join(tmp_path, "ru-hexlet-io-courses_files", expected_img_filename)
    expected_html_path = os.path.join(tmp_path, "ru-hexlet-io-courses.html")

    # Используем requests_mock, чтобы подменить запросы
    with requests_mock.Mocker() as m:
        # Подмена запроса HTML
        m.get(url, text=html_content)
        # Подмена запроса изображения
        m.get(img_url, content=img_content)
        logger.info("Проверяем скачивание изображения и замену ссылки")

        file_path = download(url, tmp_path)

        # Проверка: HTML сохранён
        assert os.path.exists(expected_html_path)
        assert file_path == expected_html_path

        # Проверка: изображение сохранено
        assert os.path.exists(expected_img_path)

        # Проверка: файл совпадает с оригиналом
        downloaded_image = Path(expected_img_path).read_bytes()
        assert downloaded_image == img_content

        with open(expected_html_path, encoding="utf-8") as file:
            html = file.read()
            logger.debug("Проверяем замену src внутри HTML")
            assert f'src="ru-hexlet-io-courses_files/{expected_img_filename}"' in html
            logger.info("Тест скачивания изображения успешно пройден")


def test_download_with_link_and_script(tmp_path):
    """Тестирование скачивания локальных link и script ресурсов"""
    url = "https://ru.hexlet.io/courses"
    html_content = '''
    <html>
      <head>
        <link href="/assets/application.css" rel="stylesheet">
        <script src="/packs/js/runtime.js"></script>
      </head>
      <body></body>
    </html>
    '''
    css_url = "https://ru.hexlet.io/assets/application.css"
    js_url = "https://ru.hexlet.io/packs/js/runtime.js"
    css_data = b"body { background: white; }"
    js_data = b"console.log('ok');"

    expected_css = "ru-hexlet-io-assets-application.css"
    expected_js = "ru-hexlet-io-packs-js-runtime.js"
    expected_dir = tmp_path / "ru-hexlet-io-courses_files"
    expected_html = tmp_path / "ru-hexlet-io-courses.html"

    with requests_mock.Mocker() as m:
        m.get(url, text=html_content)
        m.get(css_url, content=css_data)
        m.get(js_url, content=js_data)

        logger.info("Проверяем скачивание CSS и JS ресурсов")
        download(url, tmp_path)

        # Проверяем, что ресурсы скачаны
        assert (expected_dir / expected_css).exists()
        assert (expected_dir / expected_js).exists()

        # Проверяем, что содержимое совпадает
        assert (expected_dir / expected_css).read_bytes() == css_data
        assert (expected_dir / expected_js).read_bytes() == js_data

        html = expected_html.read_text(encoding="utf-8")
        logger.debug("Проверяем, что ссылки в HTML заменены на локальные пути")

        assert f'href="ru-hexlet-io-courses_files/{expected_css}"' in html
        assert f'src="ru-hexlet-io-courses_files/{expected_js}"' in html

        logger.info("Тест скачивания CSS и JS ресурсов успешно пройден")
