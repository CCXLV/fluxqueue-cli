import subprocess


def get_worker_version() -> str | None:
    """Run a system binary to get its version. Returns None if not installed or fails."""
    try:
        result = subprocess.run(
            ["fastqueue-worker", "--version"],
            check=True,
            capture_output=True,
            text=True,
        )
        return result.stdout.replace("fastqueue-worker", "").strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None
