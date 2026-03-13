
--------------------------------------------------------------------------------

[English](./README.md) | Русский

[![License](https://img.shields.io/badge/license-Apache%202-blue.svg)](LICENSE)

# [WIP] Клинически валидированный датасет видео цистоскопий при раке мочевого пузыря

Репозиторий [статьи](https://doi.org/10.5281/zenodo.18493618) с описанием датасета видео цистоскопий при раке мочевого пузыря

Вот перевод на русский язык:

## 0. Подготовка среды
Установите [pypoetry](https://python-poetry.org/docs/) и установите пакеты командой:
```bash
poetry install
```
Выполните команду `poetry env activate`, чтобы получить скрипт активации виртуального окружения. Скопируйте и выполните этот скрипт в оболочке.

## 1. Загрузка данных
Предполагая, что используется дистрибутив Linux, приведённый ниже сценарий устанавливает утилиту `zenodo_get` и загружает данные:
```bash
pip install zenodo_get
mkdir archive/
zenodo_get -o archive 18493618
unzip archive/videos.zip -d archive
```

## 2. Генерация образцов
Для визуальной проверки данных мы добавили скрипт наложения аннотаций поверх выборочных видеороликов.
Чтобы создать видеоролик с ограничительными рамками, запустите следующий скрипт:
```bash
python generate_video.py
```

## Примеры видео

https://github.com/user-attachments/assets/73397afb-ad84-45bd-a722-394f36c2f77a

https://github.com/user-attachments/assets/12490ebe-28f6-4e6b-8861-673fd531fed6

## Цитирование
```
@Article{Lekarev2026,
  title={Clinically validated annotated dataset of cystoscopy videos with bladder cancer},
  author={Lekarev, V. Yu.},
  doi={10.5281/zenodo.18493618},
  month     = Mar,
  year={2026}
}
```

## Лицензия

Этот код распространяется под лицензией [APACHE-2.0](LICENSE).
