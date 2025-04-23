from pathlib import Path
from doit.tools import create_folder

PODEST = "mood/locales"


def task_pot():
    """Re-create .pot ."""
    return {
        "actions": [f"pybabel extract -o MOOD.pot {PODEST}"],
        "file_dep": [*Path(".").glob("*.py")],
        "targets": ["MOOD.pot"],
    }


def task_po():
    """Update translations."""
    return {
        "actions": [f"pybabel update -D MOOD -d {PODEST} -l ru_RU.UTF-8 -i MOOD.pot"],
        "file_dep": ["MOOD.pot"],
        "targets": [f"{PODEST}/ru_RU.UTF-8/LC_MESSAGES/MOOD.po"],
    }


def task_mo():
    """Compile translations."""
    return {
        "actions": [
            (create_folder, [f"{PODEST}/ru_RU.UTF-8/LC_MESSAGES"]),
            f"pybabel compile -D MOOD -l ru_RU.UTF-8 -d {PODEST}",
        ],
        "file_dep": [f"{PODEST}/ru_RU.UTF-8/LC_MESSAGES/MOOD.po"],
        "targets": [f"{PODEST}/ru_RU.UTF-8/LC_MESSAGES/MOOD.mo"],
    }


def task_i18n():
    """Internalization Meta-task."""
    return {
        "actions": None,
        "task_dep": ["pot", "po", "mo"],
    }
