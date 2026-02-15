import subprocess
import requests
import time
import sys
import os

API_URL = "http://127.0.0.1:8000/merchant/M001"


def ensure_internal_api_running():
    try:
        requests.get(API_URL, timeout=2)
        print("Internal API already running")
        return
    except:
        print("Internal API not running -> starting automatically...")

    project_root = os.getcwd()

    env = os.environ.copy()
    env["PYTHONPATH"] = project_root

    subprocess.Popen(
        [
            sys.executable,
            "-m",
            "uvicorn",
            "ingestion.simulated_internal_api:app",
            "--host",
            "127.0.0.1",
            "--port",
            "8000",
        ],
        cwd=project_root,
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # wait for boot
    for _ in range(15):
        try:
            requests.get(API_URL, timeout=2)
            print("Internal API started successfully")
            return
        except:
            time.sleep(1)

    raise RuntimeError("Failed to start internal API")
