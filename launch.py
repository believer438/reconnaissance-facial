import os
import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
VENV_PYTHON = BASE_DIR / "venv" / "Scripts" / "python.exe"


def resolve_python() -> str:
    if VENV_PYTHON.exists():
        return str(VENV_PYTHON)
    return sys.executable


def run_step(args: list[str]) -> None:
    subprocess.run([resolve_python(), "manage.py", *args], cwd=BASE_DIR, check=True)


def main() -> None:
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
    run_step(["migrate", "--noinput"])
    run_step(["seed_demo_data"])
    run_step(["runserver"])


if __name__ == "__main__":
    main()
