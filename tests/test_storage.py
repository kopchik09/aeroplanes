import json

import pytest

from src.models.aeroplane import Aeroplane
from src.storage.base import AbstractAeroplaneStorage
from src.storage.db_storage import DatabaseAeroplaneStorage
from src.storage.json_storage import JSONAeroplaneStorage


@pytest.fixture
def storage(tmp_path):
    return JSONAeroplaneStorage(tmp_path / "planes.json")


def make_plane(callsign="UAL1621", country="United States"):
    return Aeroplane(callsign, country, velocity=250.0, baro_altitude=10000.0)


def test_empty_storage_returns_empty_list(storage):
    assert storage.get_aeroplanes() == []


def test_add_one_plane(storage):
    storage.add_aeroplane(make_plane("A1"))
    planes = storage.get_aeroplanes()
    assert [p.callsign for p in planes] == ["A1"]


def test_add_many_planes(storage):
    storage.add_aeroplanes([make_plane("A1"), make_plane("B2")])
    assert len(storage.get_aeroplanes()) == 2


def test_new_planes_are_appended(storage):
    storage.add_aeroplane(make_plane("A1"))
    storage.add_aeroplane(make_plane("B2"))
    assert [p.callsign for p in storage.get_aeroplanes()] == ["A1", "B2"]


def test_get_by_criteria(storage):
    storage.add_aeroplanes(
        [
            make_plane("A1", country="Spain"),
            make_plane("B2", country="France"),
        ]
    )
    result = storage.get_aeroplanes(lambda p: p.origin_country == "Spain")
    assert [p.callsign for p in result] == ["A1"]


def test_delete_by_criteria_returns_count(storage):
    storage.add_aeroplanes(
        [
            make_plane("A1", country="Spain"),
            make_plane("B2", country="France"),
            make_plane("C3", country="France"),
        ]
    )
    removed = storage.delete_aeroplanes(lambda p: p.origin_country == "France")
    assert removed == 2
    assert [p.callsign for p in storage.get_aeroplanes()] == ["A1"]


def test_delete_with_no_matches_returns_zero(storage):
    storage.add_aeroplane(make_plane("A1", country="Spain"))
    assert storage.delete_aeroplanes(lambda p: p.origin_country == "Italy") == 0


def test_data_is_written_to_json_file(storage):
    storage.add_aeroplane(make_plane("A1"))
    raw = json.loads(storage.path.read_text(encoding="utf-8"))
    assert raw[0]["callsign"] == "A1"


def test_data_survives_new_storage_object(tmp_path):
    path = tmp_path / "planes.json"
    JSONAeroplaneStorage(path).add_aeroplane(make_plane("A1"))
    planes = JSONAeroplaneStorage(path).get_aeroplanes()
    assert [p.callsign for p in planes] == ["A1"]


def test_creates_missing_folders(tmp_path):
    path = tmp_path / "nested" / "dir" / "planes.json"
    JSONAeroplaneStorage(path).add_aeroplane(make_plane())
    assert path.exists()


def test_empty_file_means_empty_storage(tmp_path):
    path = tmp_path / "planes.json"
    path.write_text("", encoding="utf-8")
    assert JSONAeroplaneStorage(path).get_aeroplanes() == []


def test_close_does_not_fail(storage):
    storage.close()


def test_abstract_storage_cannot_be_created():
    with pytest.raises(TypeError):
        AbstractAeroplaneStorage()


def test_db_stub_raises_not_implemented():
    with pytest.raises(NotImplementedError):
        DatabaseAeroplaneStorage().get_aeroplanes()
