from pathlib import Path


ENV_PATH = Path(__file__).resolve().parent.parent / ".env"


def load_dotenv() -> None:
    if not ENV_PATH.exists():
        return

    for raw_line in ENV_PATH.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')

        if not key:
            continue

        # Respeta variables ya definidas en el entorno del proceso.
        import os

        os.environ.setdefault(key, value)
