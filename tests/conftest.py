import os
import shutil
import subprocess
import time
from pathlib import Path
import pytest

import requests
from tests.utils import DEVNULL, HOST, DEFAULT_STDOUT

server_process: subprocess.Popen


def pytest_sessionstart(session):
    global server_process

    if os.path.isdir("src/main/migrations"):
        shutil.rmtree("src/main/migrations")
    Path("db.sqlite3").unlink(missing_ok=True)
    subprocess.run(
        ["python", "src/manage.py", "makemigrations", "main"],
        stdout=DEVNULL,
        stderr=DEVNULL,
    )
    subprocess.run(
        ["python", "src/manage.py", "migrate"],
        stdout=DEVNULL,
        stderr=DEVNULL,
    )

    server_process = subprocess.Popen(
        ["python", "src/manage.py", "runserver"],
        stdout=DEVNULL,
        stderr=DEVNULL,
    )

    for _ in range(10):
        time.sleep(0.2)
        try:
            response = requests.get(f"{HOST}/utils/ready")
        except Exception:
            pass
        else:
            if response.status_code == 200:
                break
    else:
        pytest.exit("Failed to establish a new connection", returncode=1)


def pytest_sessionfinish(session, exitstatus):
    server_process.terminate()
