import os
import argparse
from page_loader.page_loader import download


def main():
    parser = argparse.ArgumentParser(description="Page Loader: скачивает веб-страницу")
    parser.add_argument("url", help="URL страницы для загрузки")
    parser.add_argument("-o", "--output", help="Директория для сохранения", default=os.getcwd())

    args = parser.parse_args()

    try:
        file_path = download(args.url, args.output)
        print(file_path)
    except Exception as e:
        print(f"Ошибка: {e}")
        exit(1)


if __name__ == "__main__":
    main()
