import shutil
from pathlib import Path
from doit.tools import create_folder

# По умолчанию собираем html-документацию
DOIT_CONFIG = {
    "default_tasks": ["html"],
}

# Пути к исходникам и локалям
SRC_DIR = Path("mood")
LOCALE_DIR = Path("mood/locales")
DOC_SRC = Path("docs/source")
BUILD_ROOT = DOC_SRC.parent / "build"
BUILD_HTML = BUILD_ROOT / "html"


def task_pot():
    """Извлечь шаблон переводов (.pot) только при изменении исходников."""
    return {
        "actions": [f"pybabel extract -o MOOD.pot {SRC_DIR.as_posix()}"],
        "file_dep": [str(p) for p in SRC_DIR.rglob("*.py")],
        "targets": ["MOOD.pot"],
        "clean": True,
    }


def task_po():
    """Обновить .po-файл."""
    po_path = LOCALE_DIR / "ru_RU.UTF-8" / "LC_MESSAGES" / "MOOD.po"
    return {
        "actions": [
            f"pybabel update -D MOOD -d {LOCALE_DIR.as_posix()} -l ru_RU.UTF-8 -i MOOD.pot"
        ],
        "file_dep": ["MOOD.pot"],
        "targets": [str(po_path)],
        "clean": True,
    }


def task_mo():
    """Скомпилировать .po → .mo."""
    locale_subdir = LOCALE_DIR / "ru_RU.UTF-8" / "LC_MESSAGES"
    mo_path = locale_subdir / "MOOD.mo"
    return {
        "actions": [
            (create_folder, [str(locale_subdir)]),
            f"pybabel compile -D MOOD -l ru_RU.UTF-8 -d {LOCALE_DIR.as_posix()}",
        ],
        "file_dep": [str(locale_subdir / "MOOD.po")],
        "targets": [str(mo_path)],
        "clean": True,
    }


def task_i18n():
    """Собрать все шаги перевода (extract, update, compile)."""
    return {
        "actions": None,
        "task_dep": ["pot", "po", "mo"],
    }


def task_html():
    """Собрать HTML-документацию Sphinx."""
    static_dir = DOC_SRC / "_static"
    return {
        "actions": [
            (shutil.rmtree, [str(BUILD_ROOT)], {"ignore_errors": True}),
            (create_folder, [str(static_dir)]),
            f"sphinx-build -b html {DOC_SRC.as_posix()} {BUILD_HTML.as_posix()}",
        ],
        "file_dep": (
            [str(p) for p in DOC_SRC.rglob("*.rst")]
            + [str(p) for p in DOC_SRC.rglob("*.py")]
            + ["docs/Makefile"]
        ),
        "targets": [str(BUILD_ROOT)],
        "clean": [(shutil.rmtree, [str(BUILD_ROOT)], {"ignore_errors": True})],
    }


def task_test():
    """Запустить клиентские и серверные тесты (зависит от i18n)."""
    return {
        "actions": [
            "python3 -m mood.tests.client_test -v",
            "python3 -m mood.tests.server_test -v",
        ],
        "task_dep": ["i18n"],
    }
