from pathlib import Path

from src.api.adapters import OpenSkyNominatimAdapter
from src.service import AeroplaneService
from src.storage.json_storage import JSONAeroplaneStorage
from src.ui import user_interaction

DEFAULT_DATA_FILE = Path("data") / "aeroplanes.json"


def build_service(data_file: Path = DEFAULT_DATA_FILE) -> AeroplaneService:
    """Собирает все части программы в одном месте."""
    return AeroplaneService(
        api=OpenSkyNominatimAdapter(),
        storage=JSONAeroplaneStorage(data_file),
    )


def main() -> None:
    user_interaction(build_service())


if __name__ == "__main__":
    main()
