from src.api.adapters import OpenSkyNominatimAdapter
from src.service import AeroplaneService
from src.storage.json_storage import JSONAeroplaneStorage
from src.ui import user_interaction


def main() -> None:
    service = AeroplaneService(
        api=OpenSkyNominatimAdapter(),
        storage=JSONAeroplaneStorage("data/aeroplanes.json"),
    )
    user_interaction(service)


if __name__ == "__main__":
    main()
