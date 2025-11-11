### Hexlet tests and linter status:
[![Actions Status](https://github.com/KMats11/python-pytest-testing-project-79/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/KMats11/python-pytest-testing-project-79/actions)

[![Maintainability](https://qlty.sh/gh/KMats11/projects/python-pytest-testing-project-79/maintainability.svg)](https://qlty.sh/gh/KMats11/projects/python-pytest-testing-project-79)
[![Code Coverage](https://qlty.sh/gh/KMats11/projects/python-pytest-testing-project-79/coverage.svg)](https://qlty.sh/gh/KMats11/projects/python-pytest-testing-project-79)


# Page Loader
Утилита для скачивания веб-страниц вместе с локальными ресурсами (img, link, script).

## Установка

Установите пакет локально в editable режиме:

```bash
pip install -e .
```

## Пример использования

Скачивание страницы (https://ru.hexlet.io/courses) в текущую директорию:

```bash
page-loader https://ru.hexlet.io/courses
```

Скачивание страницы (https://ru.hexlet.io/courses) в указанную директорию:

```bash
page-loader https://ru.hexlet.io/courses -o D:\testing
```

После выполнения команд в директории появится HTML-файл и папка с ресурсами:

```
ru-hexlet-io-courses.html
ru-hexlet-io-courses_files/
```


## Логирование

Приложение использует встроенный модуль Python `logging` для информативного вывода сообщений о процессе работы:

- `INFO` — ключевые события работы
- `WARNING` — предупреждения, например о неудачных скачиваниях ресурсов
- `DEBUG` — подробные сообщения для отладки
- `ERROR` — ошибки HTTP-запросов и критичные сбои

По умолчанию выводятся сообщения `INFO` и выше.  
Для подробного `DEBUG`-вывода можно изменить уровень логирования через переменные окружения или в настройках pytest.


## Демонстрация работы

Ниже показан пример работы утилиты, включая успешную загрузку и обработку ошибки:

![Демонстрация работы Page Loader](page_loader_demo.gif)
