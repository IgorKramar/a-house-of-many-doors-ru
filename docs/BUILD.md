# Сборочная лаборатория

Потребуется собственная Windows/Steam-копия версии 2.3, UndertaleModCli **0.9.2**, Python **3.11+**, Pillow и исходный вариативный Cormorant Garamond. Шрифты Georgia берутся из установленной Windows. Бинарные инструменты и шрифты в репозиторий не включены.

Последняя подтверждённая сборка сделана в частной лаборатории. Эти инструкции описывают её маршрут; чистый публичный клон пока не прошёл полный сборочный цикл.

## 1. Частные входные данные

В корне клона создайте каталоги `work/original`, `work/source`, `work/build/fonts`, `work/build/gml`, `work/fonts`, `work/tools/utmt`. В `work/original/data.win` поместите копию неизменённого архива своей игры. В `work/tools/utmt` разместите UndertaleModCli с его зависимостями.

Контрольная сумма поддерживаемого оригинала:

```text
SHA-256 DBC01DCF416E6002298531C1A0E707BD3FF64F0AFA70BBA1EAB6F527709F0160
```

Другой хеш требует проверки версии и всех ссылок, а не обхода контроля. Установленный старый прототип не подходит в качестве оригинала.

## 2. Локальное извлечение

Все команды выполняются из корня репозитория. Результаты остаются в игнорируемом `work/source`.

```powershell
python -m pip install -r requirements.txt
work/tools/utmt/UndertaleModCli.exe dump work/original/data.win -o work/source -c UMT_DUMP_ALL
work/tools/utmt/UndertaleModCli.exe load work/original/data.win -s work/scripts/export_strings.csx
work/tools/utmt/UndertaleModCli.exe load work/original/data.win -s work/scripts/inspect.csx
work/tools/utmt/UndertaleModCli.exe load work/original/data.win -s work/scripts/inspect_ui_assets.csx
python work/scripts/extract_batch.py
```

`dump -s` создаёт плоский strings.txt и не заменяет JSON-метаданные экспортёра. CodeEntries создаёт CLI при выгрузке кода. Экспорт всех сценариев может занять время.

## 3. Шрифты и перевод

Поместите вариативный шрифт в `work/fonts/CormorantGaramond.ttf`. Контрольная сумма использованного файла записана в [status.json](status.json). Его условия SIL Open Font License сохраняются; Georgia используется локально по условиям Windows и не публикуется.

```powershell
python work/scripts/make_fonts.py
python work/scripts/prepare_translation.py
python work/scripts/check_translation.py
```

Подготовка перевода автоматически создаёт типографику интерфейса. Скрипты `generated_*.py` собирают полные фразы и варианты, а не отдельные несклоняемые обрывки.

## 4. Проверка и рабочий бинарный файл

```powershell
python work/scripts/validate_interface.py
python work/scripts/validate_tybalt_events.py
python work/scripts/validate_violante_events.py
work/tools/utmt/UndertaleModCli.exe load work/original/data.win -s work/scripts/build.csx -o work/build/data.win --overwrite
work/tools/utmt/UndertaleModCli.exe load work/build/data.win -s work/scripts/validate.csx
```

Другие `validate_*` проверяют соответствующие переводческие блоки. Применять `--overwrite` можно только к рабочему выходному файлу. Каждый новый бинарный файл собирается из оригинала, а не из предыдущего патча.

## 5. Выпуск и установка

Готового патча и установщика пока нет. Установка рабочей сборки и игровой прогон отложены до завершения перевода. Будущий выпуск должен содержать отдельный BPS/xdelta-патч, проверку исходного хеша, резервную копию и откат, а не полный data.win.
