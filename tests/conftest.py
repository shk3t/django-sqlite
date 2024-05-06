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
        ["python", "src/manage.py", "migrate"], stdout=DEVNULL, stderr=DEVNULL
    )

    server_process = subprocess.Popen(
        ["python", "src/manage.py", "runserver"],
        stdout=DEVNULL,
        stderr=DEVNULL,
    )

    try:
        response = requests.get(f"{HOST}/utils/ready", timeout=200)
        if 200 < response.status_code >= 300:
            raise Exception("Bad status code")
    except Exception as error:
        pytest.exit(str(error), returncode=1)


def pytest_sessionfinish(session, exitstatus):
    server_process.terminate()