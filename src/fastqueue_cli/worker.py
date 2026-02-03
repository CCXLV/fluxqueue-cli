import os
import platform
import re
import shutil
import sys
import tarfile

import requests
from dotenv import load_dotenv

from fastqueue_cli.exceptions import (
    AlreadyInstalledError,
    BinaryNotFoundError,
    InvalidVersionError,
    ReleaseNotFoundError,
)
from fastqueue_cli.utils.worker import get_worker_version

load_dotenv()

REPO = "CCXLV/fastqueue"
BINARY_NAME = "fastqueue-worker"
INSTALL_DIR = "/usr/local/bin" if platform.system() != "Windows" else "C:\\bin"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# TODO: Refactor the headers since the token won't be needed when launched to public


def get_worker_release(version: str | None = None):
    version_pattern = r"^worker-v(\d+\.\d+\.\d+)$"

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json",
    }
    api_url = f"https://api.github.com/repos/{REPO}/releases"
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()

    worker_releases = []
    for r in response.json():
        match = re.match(version_pattern, r["tag_name"])
        if match:
            r["extracted_version"] = match.group(1)
            worker_releases.append(r)

    if not worker_releases:
        raise ReleaseNotFoundError("No worker releases found.")

    if version:
        for r in worker_releases:
            if r["extracted_version"] == version:
                return r
        available = [r["extracted_version"] for r in worker_releases]
        raise InvalidVersionError(
            f"Worker version {version} not found.\n"
            f"Available versions: {', '.join(available)}"
        )
    return worker_releases[0]


def download_and_install(version: str | None = None):
    if shutil.which("fastqueue-worker"):
        if version:
            worker_version = get_worker_version()
            if worker_version != version:
                # TODO: Finish this
                pass

        raise AlreadyInstalledError(
            "fastqueue-worker is already installed, use fastqueue update command if you want to update it."
        )

    release = get_worker_release(version)
    version = release["tag_name"]

    py_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    system = platform.system().lower()

    print(f"Detected: Python {py_version} on {system}")
    print(f"Fetching latest worker: {version}")
    asset_api_url = None
    target_name = None
    for asset in release["assets"]:
        name = asset["name"]
        if f"py{py_version}" in name and system in name:
            asset_api_url = asset["url"]
            target_name = name
            break

    if not asset_api_url or not target_name:
        raise BinaryNotFoundError(
            f"No binary found for Python {py_version} on {system}."
        )

    print(f"Downloading {target_name} via API...")

    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/octet-stream",
    }

    try:
        r = requests.get(asset_api_url, headers=headers, stream=True)
    except:
        delete_installed_files(target_name)
        raise

    with open(target_name, "wb") as f:
        shutil.copyfileobj(r.raw, f)

    if target_name.endswith(".tar.gz"):
        with tarfile.open(target_name, "r:gz") as tar:
            try:
                tar.extractall(path=".", filter="data")

                os.chmod(BINARY_NAME, 0o755)

                dest_path = os.path.join(INSTALL_DIR, BINARY_NAME)
                shutil.copy2(BINARY_NAME, dest_path)
                delete_installed_files(target_name)
            except:
                delete_installed_files(target_name)
                raise

    print(f"Successfully installed {BINARY_NAME} to {INSTALL_DIR}")


def delete_installed_files(target_name: str):
    os.remove(BINARY_NAME)
    os.remove(target_name)
