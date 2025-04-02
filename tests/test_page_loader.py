import os
import tempfile
import pytest
import requests_mock
from page_loader.page_loader import make_filename, download


@pytest.fixture
def temp_dir():
    """Фикстура для создания временной директории"""
    with tempfile.TemporaryDirectory() as tmpdirname:
        yield tmpdirname


def test_make_filename():
    """Тестирование создания имени файла из URL"""
    assert make_filename("https://ru.hexlet.io/courses") == "ru-hexlet-io-courses.html"
    assert make_filename("http://example.com/path/page") == "example-com-path-page.html"
    assert make_filename("https://test.com/some-page?query=1") == "test-com-some-page-query-1.html"


def test_download(temp_dir):
    """Тестирование скачивания страницы"""
    url = "https://ru.hexlet.io/courses"
    test_page_text = "<html><body>Test Page</body></html>"
    expected_filename = os.path.join(temp_dir, "ru-hexlet-io-courses.html")

    with requests_mock.Mocker() as m:
        m.get(url, text=test_page_text)  # Подмена запроса

        file_path = download(url, temp_dir)

        # Проверка, что файл создан
        assert os.path.exists(file_path)
        assert file_path == expected_filename

        # Проверка содержимое файла
        with open(file_path, encoding="utf-8") as file:
            content = file.read()
            assert content == test_page_text

        # Проверка, что requests.get(url) был вызван ОДИН раз
        assert len(m.request_history) == 1
        # Проверка,что запрос был сделан по нужному URL
        assert m.request_history[0].url == url
        # Проверка,что это именно GET-запрос
        assert m.request_history[0].method == "GET"
