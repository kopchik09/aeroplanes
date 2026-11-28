from src.api.base import AbstractAPIAdapter
from src.service import AeroplaneService
from src.storage.json_storage import JSONAeroplaneStorage
from src.storage.base import AbstractAeroplaneStorage


class InMemoryAeroplaneStorage(AbstractAeroplaneStorage):
    """Хранилище в памяти. Нужно, чтобы проверить: новый коннектор подключается без правок service."""

    def __init__(self):
        self._planes = []

    def add_aeroplanes(self, aeroplanes):
        self._planes.extend(aeroplanes)

    def get_aeroplanes(self, criteria=None):
        return [p for p in self._planes if criteria is None or criteria(p)]

    def delete_aeroplanes(self, criteria):
        kept = [p for p in self._planes if not criteria(p)]
        removed = len(self._planes) - len(kept)
        self._planes = kept
        return removed

    def close(self):
        pass


def make_state(icao24, callsign, country, altitude, velocity, on_ground=False):
    """Собирает массив из 17 полей, как его отдаёт OpenSky."""
    return [
        icao24,
        callsign,
        country,
        0,
        0,
        0.0,
        0.0,
        altitude,
        on_ground,
        velocity,
        0.0,
        0.0,
        None,
        altitude,
        "0000",
        False,
        0,
    ]


def sample_states():
    return [
        make_state("4b1812", "SWR438A ", "Switzerland", 4267.2, 189.7),
        make_state("3c6751", "DLH1QM  ", "Germany", 10668.0, 245.1),
        make_state("a1b2c3", "IBE123  ", "Spain", 11500.0, 230.0),
        make_state("d4e5f6", "TAXI1   ", "Spain", 0.0, 10.0, on_ground=True),
    ]


class FakeAPI(AbstractAPIAdapter):
    """Вместо интернета отдаёт заранее заготовленные состояния самолётов."""

    def __init__(self, states=None):
        self.states = states or []
        self.requested_countries = []

    def get_country_bbox(self, country):
        self.requested_countries.append(country)
        return (0.0, 1.0, 0.0, 1.0)

    def get_aeroplanes_in_bbox(self, bbox):
        return self.states


def make_service(tmp_path, states=None):
    """Сервис с фальшивым API и временным JSON-файлом внутри tmp_path."""
    return AeroplaneService(
        api=FakeAPI(states),
        storage=JSONAeroplaneStorage(tmp_path / "planes.json"),
    )
