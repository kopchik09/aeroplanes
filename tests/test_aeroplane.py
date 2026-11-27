import pytest

from src.api.aeroplane import Aeroplane


def make_plane(
    callsign="UAL1621",
    country="United States",
    velocity=268.79,
    altitude=10203.18,
    **kwargs,
):
    return Aeroplane(callsign, country, velocity, altitude, **kwargs)


# ---------- создание и проверка данных ----------


def test_creates_plane_with_valid_data():
    plane = make_plane()
    assert plane.callsign == "UAL1621"
    assert plane.origin_country == "United States"
    assert plane.velocity == 268.79
    assert plane.baro_altitude == 10203.18
    assert plane.on_ground is False


def test_callsign_is_stripped():
    assert make_plane(callsign="SWR438A ").callsign == "SWR438A"


@pytest.mark.parametrize("callsign", ["", "   "])
def test_empty_callsign_is_rejected(callsign):
    with pytest.raises(ValueError):
        make_plane(callsign=callsign)


def test_negative_velocity_is_rejected():
    with pytest.raises(ValueError):
        make_plane(velocity=-1)


def test_velocity_must_be_number():
    with pytest.raises(TypeError):
        make_plane(velocity="fast")


def test_bool_is_not_accepted_as_number():
    with pytest.raises(TypeError):
        make_plane(altitude=True)


def test_altitude_out_of_range_is_rejected():
    with pytest.raises(ValueError):
        make_plane(altitude=100000)


def test_invalid_icao24_is_rejected():
    with pytest.raises(ValueError):
        make_plane(icao24="xyz")


def test_icao24_is_lowercased():
    assert make_plane(icao24="4B1812").icao24 == "4b1812"


def test_invalid_change_is_not_saved():
    plane = make_plane()
    with pytest.raises(ValueError):
        plane.velocity = -5
    assert plane.velocity == 268.79


# ---------- сравнение ----------


def test_compare_speed():
    fast = make_plane(velocity=250)
    slow = make_plane(velocity=200)
    assert fast.compare_speed(slow) == 1
    assert slow.compare_speed(fast) == -1
    assert fast.compare_speed(make_plane(velocity=250)) == 0


def test_compare_altitude():
    high = make_plane(altitude=10000)
    low = make_plane(altitude=5000)
    assert high.compare_altitude(low) == 1
    assert low.compare_altitude(high) == -1


def test_sorting_by_altitude():
    planes = [
        make_plane(altitude=5000),
        make_plane(altitude=12000),
        make_plane(altitude=9000),
    ]
    assert [p.baro_altitude for p in sorted(planes)] == [5000, 9000, 12000]


def test_compare_with_non_plane_raises():
    with pytest.raises(TypeError):
        make_plane().compare_speed(100)


# ---------- данные из OpenSky ----------


def test_from_state_reads_opensky_array():
    state = [
        "4b1812",
        "SWR438A ",
        "Switzerland",
        1766166618,
        1766166618,
        -0.0168,
        51.0888,
        4267.2,
        False,
        189.7,
        129.39,
        14.63,
        None,
        4282.44,
        "2061",
        False,
        0,
    ]
    plane = Aeroplane.from_state(state)
    assert plane.icao24 == "4b1812"
    assert plane.callsign == "SWR438A"
    assert plane.origin_country == "Switzerland"
    assert plane.baro_altitude == 4267.2
    assert plane.velocity == 189.7
    assert plane.on_ground is False


def test_from_state_handles_missing_values():
    state = ["4b1812", None, "Spain", None, None, None, None, None, True, None]
    plane = Aeroplane.from_state(state)
    assert plane.callsign == "UNKNOWN"
    assert plane.baro_altitude == 0.0
    assert plane.velocity == 0.0
    assert plane.on_ground is True


def test_cast_to_object_list():
    states = [
        ["4b1812", "SWR438A ", "Switzerland", 0, 0, 0, 0, 4267.2, False, 189.7],
        ["3c6751", "DLH1QM  ", "Germany", 0, 0, 0, 0, 10668.0, False, 245.1],
    ]
    planes = Aeroplane.cast_to_object_list(states)
    assert [p.origin_country for p in planes] == ["Switzerland", "Germany"]


def test_dict_roundtrip():
    plane = make_plane(icao24="4b1812", on_ground=True)
    assert Aeroplane.from_dict(plane.to_dict()).to_dict() == plane.to_dict()
