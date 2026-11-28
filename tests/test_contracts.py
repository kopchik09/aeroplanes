import pytest

from src.models.aeroplane import Aeroplane
from src.service import AeroplaneService
from src.storage.base import AbstractAeroplaneStorage
from src.storage.json_storage import JSONAeroplaneStorage
from tests.helpers import FakeAPI, InMemoryAeroplaneStorage, sample_states


@pytest.fixture(params=["json", "memory"])
def storage(request, tmp_path):
    if request.param == "json":
        return JSONAeroplaneStorage(tmp_path / "planes.json")
    return InMemoryAeroplaneStorage()


def make_plane(callsign, country):
    return Aeroplane(callsign, country, velocity=200.0, baro_altitude=9000.0)


def test_implements_the_contract(storage):
    assert isinstance(storage, AbstractAeroplaneStorage)


def test_empty_storage(storage):
    assert storage.get_aeroplanes() == []


def test_add_and_get_all(storage):
    storage.add_aeroplanes([make_plane("A1", "Spain"), make_plane("B2", "France")])
    assert sorted(p.callsign for p in storage.get_aeroplanes()) == ["A1", "B2"]


def test_get_by_criteria(storage):
    storage.add_aeroplanes([make_plane("A1", "Spain"), make_plane("B2", "France")])
    result = storage.get_aeroplanes(lambda p: p.origin_country == "Spain")
    assert [p.callsign for p in result] == ["A1"]


def test_delete_returns_number_removed(storage):
    storage.add_aeroplanes([make_plane("A1", "Spain"), make_plane("B2", "France")])
    assert storage.delete_aeroplanes(lambda p: p.origin_country == "France") == 1
    assert [p.callsign for p in storage.get_aeroplanes()] == ["A1"]


def test_delete_nothing_returns_zero(storage):
    storage.add_aeroplane(make_plane("A1", "Spain"))
    assert storage.delete_aeroplanes(lambda p: False) == 0


def test_service_works_with_any_storage(storage):
    service = AeroplaneService(api=FakeAPI(sample_states()), storage=storage)
    assert service.load_country("Spain") == 4
    assert [p.baro_altitude for p in service.top_by_altitude(2)] == [11500.0, 10668.0]
