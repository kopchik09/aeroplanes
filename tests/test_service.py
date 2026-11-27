import pytest

from tests.helpers import make_service, sample_states


def test_load_country_saves_planes(tmp_path):
    service = make_service(tmp_path, sample_states())
    count = service.load_country("Spain")
    assert count == 4
    assert service.api.requested_countries == ["Spain"]
    assert len(service.storage.get_aeroplanes()) == 4


def test_loading_same_country_twice_does_not_duplicate(tmp_path):
    service = make_service(tmp_path, sample_states())
    service.load_country("Spain")
    service.load_country("Spain")
    assert len(service.storage.get_aeroplanes()) == 4


def test_top_by_altitude_returns_highest_first(tmp_path):
    service = make_service(tmp_path, sample_states())
    service.load_country("Spain")
    top = service.top_by_altitude(2)
    assert [p.baro_altitude for p in top] == [11500.0, 10668.0]


def test_top_n_larger_than_storage_returns_all(tmp_path):
    service = make_service(tmp_path, sample_states())
    service.load_country("Spain")
    assert len(service.top_by_altitude(10)) == 4


def test_by_registration_ignores_case_and_accepts_many(tmp_path):
    service = make_service(tmp_path, sample_states())
    service.load_country("Spain")
    result = service.by_registration(["spain", " Switzerland "])
    assert sorted(p.callsign for p in result) == ["IBE123", "SWR438A", "TAXI1"]


def test_by_altitude_range_includes_bounds(tmp_path):
    service = make_service(tmp_path, sample_states())
    service.load_country("Spain")
    result = service.by_altitude_range(4267.2, 10668.0)
    assert [p.baro_altitude for p in result] == [10668.0, 4267.2]


def test_altitude_range_with_swapped_bounds_raises(tmp_path):
    service = make_service(tmp_path, sample_states())
    with pytest.raises(ValueError):
        service.by_altitude_range(10000, 5000)


def test_remove_on_ground_deletes_only_grounded(tmp_path):
    service = make_service(tmp_path, sample_states())
    service.load_country("Spain")
    assert service.remove_on_ground() == 1
    assert len(service.get_all()) == 3


def test_get_all_sorted_by_altitude_desc(tmp_path):
    service = make_service(tmp_path, sample_states())
    service.load_country("Spain")
    assert [p.baro_altitude for p in service.get_all()] == [
        11500.0,
        10668.0,
        4267.2,
        0.0,
    ]
