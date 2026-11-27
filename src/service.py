from src.api.base import AbstractAPIAdapter
from src.models.aeroplane import Aeroplane
from src.storage.base import AbstractAeroplaneStorage


class AeroplaneService:
    """Связывает API и хранилище. Интерфейс работает только с этим классом."""

    def __init__(
        self, api: AbstractAPIAdapter, storage: AbstractAeroplaneStorage
    ) -> None:
        self.api = api
        self.storage = storage

    def load_country(self, country: str) -> int:
        """Загружает самолёты над страной и сохраняет их.

        Если самолёт с таким icao24 уже есть в хранилище, старая запись заменяется,
        поэтому повторная загрузка не создаёт дубликаты.
        """
        planes = Aeroplane.cast_to_object_list(self.api.get_aeroplanes(country))
        fresh_ids = {plane.icao24 for plane in planes if plane.icao24}
        self.storage.delete_aeroplanes(lambda plane: plane.icao24 in fresh_ids)
        self.storage.add_aeroplanes(planes)
        return len(planes)

    def get_all(self) -> list[Aeroplane]:
        """Все сохранённые самолёты, от самого высокого к самому низкому."""
        return sorted(self.storage.get_aeroplanes(), reverse=True)

    def top_by_altitude(self, n: int) -> list[Aeroplane]:
        return self.get_all()[:n]

    def by_registration(self, countries: list[str]) -> list[Aeroplane]:
        wanted = {name.strip().lower() for name in countries if name.strip()}
        planes = self.storage.get_aeroplanes(
            lambda plane: plane.origin_country.lower() in wanted
        )
        return sorted(planes, reverse=True)

    def by_altitude_range(self, low: float, high: float) -> list[Aeroplane]:
        if low > high:
            raise ValueError("Минимальная высота больше максимальной")
        planes = self.storage.get_aeroplanes(
            lambda plane: low <= plane.baro_altitude <= high
        )
        return sorted(planes, reverse=True)

    def remove_on_ground(self) -> int:
        return self.storage.delete_aeroplanes(lambda plane: plane.on_ground)
