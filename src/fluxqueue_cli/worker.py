import os
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path

import requests

from fluxqueue_cli.exceptions import (
    AlreadyInstalledError,
    BinaryNotFoundError,
    InvalidVersionError,
    NotInstalledError,
    ReleaseNotFoundError,
)

REPO = "CCXLV/fluxqueue"
BINARY_NAME = "fluxqueue-worker"
if platform.system() == "Windows":
    user_profile = os.environ.get("USERPROFILE", os.path.expanduser("~"))
    install_dir = os.path.join(user_profile, ".fluxqueue", "bin")
    INSTALL_DIR = install_dir
else:
    INSTALL_DIR = "/usr/local/bin"

# TODO: Add startup wrapper support


def start_worker(
    *,
    concurrency: int,
    redis_url: str,
    tasks_module_path: str,
    queue: str,
    save_dead_tasks=False,
):
    # fmt: off
    arguments = [
        "--concurrency", str(concurrency),
        "--redis-url", redis_url,
        "--tasks-module-path", tasks_module_path,
        "--queue", queue,
    ]
    # fmt: on

    if save_dead_tasks:
        arguments.append("--save-dead-tasks")

    subprocess.run(
        ["fluxqueue-worker", *arguments],
        stdin=sys.stdin,
        stdout=sys.stdout,
        stderr=sys.stderr,
    )


def get_worker_version() -> str | None:
    try:
        result = subprocess.run(
            ["fluxqueue-worker", "--version"],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.replace("fluxqueue-worker", "").strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def get_worker_release(version: str | None = None):
    headers = {
        "Accept": "application/vnd.github.v3+json",
    }
    api_url = f"https://api.github.com/repos/{REPO}/releases"
    response = requests.get(api_url, headers=headers)
    response.raise_for_status()

    worker_releases = []
    for r in response.json():
        tag = r["tag_name"]
        if tag.startswith("worker-v"):
            version_str = tag[len("worker-v") :]
            r["extracted_version"] = version_str
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


def download_worker_binary(version: str | None = None):
    release = get_worker_release(version)
    version = release["extracted_version"]

    py_version = f"{sys.version_info.major}.{sys.version_info.minor}"
    system = platform.system().lower()

    print(f"Detected: Python {py_version} on {system}")
    print(f"Fetching latest worker: {version}")
    asset_api_url = None
    target_name: str | None = None
    for asset in release["assets"]:
        name = asset["name"]
        if f"py{py_version}" in name and system in name:
            asset_api_url = asset["url"]
            target_name = str(name)
            break

    if not asset_api_url or not target_name:
        raise BinaryNotFoundError(
            f"No binary found for Python {py_version} on {system}."
        )

    print(f"Downloading {target_name} via API...")

    headers = {
        "Accept": "application/octet-stream",
    }

    try:
        r = requests.get(asset_api_url, headers=headers, stream=True)
        r.raise_for_status()
    except:
        delete_installed_files(target_name)
        raise

    with tempfile.NamedTemporaryFile(prefix=target_name, delete=False) as f:
        temp_path = Path(f.name)
        shutil.copyfileobj(r.raw, f)

    return str(temp_path), target_name


def install_worker(*, actual_file_name: str, temp_file_path: str, overwrite=False):
    if platform.system() == "Windows":
        dest_path = Path(INSTALL_DIR) / f"{BINARY_NAME}.exe"
    else:
        dest_path = Path(INSTALL_DIR) / BINARY_NAME
    if dest_path.exists() and not overwrite:
        raise FileExistsError(f"fluxqueue-worker is already installed at {dest_path}")

    # Linux
    if actual_file_name.endswith(".tar.gz"):
        with tarfile.open(temp_file_path, "r:gz") as tar:
            try:
                tar.extractall(path=".", filter="data")

                os.chmod(BINARY_NAME, 0o755)

                shutil.copy2(BINARY_NAME, dest_path)
                delete_installed_files(temp_file_path)
            except:
                delete_installed_files(temp_file_path)
                raise
    # macOS + Windows
    elif actual_file_name.endswith(".zip"):
        with tempfile.TemporaryDirectory() as extract_temp_dir:
            with zipfile.ZipFile(temp_file_path, "r") as zip_file:
                zip_file.extractall(extract_temp_dir)

            exe_name = (
                f"{BINARY_NAME}.exe" if platform.system() == "Windows" else BINARY_NAME
            )
            found_binary = None

            for root, _dirs, files in os.walk(extract_temp_dir):
                if exe_name in files:
                    found_binary = Path(root) / exe_name
                    break

            if not found_binary:
                for root, _dirs, files in os.walk(extract_temp_dir):
                    for file in files:
                        if BINARY_NAME in file and (
                            platform.system() != "Windows" or file.endswith(".exe")
                        ):
                            found_binary = Path(root) / file
                            break
                    if found_binary:
                        break

            if not found_binary:
                try:
                    os.remove(temp_file_path)
                except PermissionError:
                    raise PermissionError(
                        f"Permission denied: Could not remove temporary file {temp_file_path}. "
                        "Please remove it manually."
                    ) from None
                except OSError as e:
                    if e.errno == 13:  # Permission denied (EACCES)
                        raise PermissionError(
                            f"Permission denied: Could not remove temporary file {temp_file_path}. "
                            "Please remove it manually."
                        ) from e
                raise BinaryNotFoundError(
                    f"Could not find {exe_name} in the downloaded archive."
                )

            dest_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(found_binary, dest_path)

            if platform.system() != "Windows":
                os.chmod(dest_path, 0o755)
        try:
            os.remove(temp_file_path)
        except PermissionError:
            raise PermissionError(
                f"Permission denied: Could not remove temporary file {temp_file_path}. "
                "Please remove it manually."
            ) from None
        except OSError as e:
            if e.errno == 13:  # Permission denied (EACCES)
                raise PermissionError(
                    f"Permission denied: Could not remove temporary file {temp_file_path}. "
                    "Please remove it manually."
                ) from e
            raise
    else:
        delete_installed_files(temp_file_path)
        raise NotImplementedError("Only .tar.gz installation is implemented yet.")

    print(f"Successfully installed {BINARY_NAME} to {INSTALL_DIR}")


def download_and_install(version: str | None = None, path: str | None = None):
    if shutil.which("fluxqueue-worker"):
        raise AlreadyInstalledError(
            "fluxqueue-worker is already installed, use `fluxqueue worker update` command to update it."
        )

    temp_path, target_name = download_worker_binary(version)
    install_worker(actual_file_name=target_name, temp_file_path=temp_path)


def update_worker(*, version: str | None = None, no_backup: bool = False):
    current_version = get_worker_version()

    if not current_version:
        raise NotInstalledError(
            "fluxqueue-worker is not installed. Use `fluxqueue worker install` to install it."
        )

    print(f"Current Version: {current_version}")
    if version:
        print(f"Desired Version: {version}")

    if platform.system() == "Windows":
        dest_path = os.path.join(INSTALL_DIR, f"{BINARY_NAME}.exe")
        backup_suffix = ".exe.backup"
    else:
        dest_path = os.path.join(INSTALL_DIR, BINARY_NAME)
        backup_suffix = ".backup"

    if not no_backup:
        new_name = os.path.join(
            INSTALL_DIR, f"{BINARY_NAME}-{current_version}{backup_suffix}"
        )
        os.rename(dest_path, new_name)

    temp_path, target_name = download_worker_binary(version)
    install_worker(
        actual_file_name=target_name,
        temp_file_path=temp_path,
        overwrite=no_backup,
    )


def delete_installed_files(temp_path: str):
    os.remove(BINARY_NAME)
    os.remove(temp_path)
