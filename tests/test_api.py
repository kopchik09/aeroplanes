from unittest.mock import MagicMock

import pytest
import requests

from src.api.adapters import CountryNotFoundError, OpenSkyNominatimAdapter
from src.api.base import APIError


def make_session(*payloads):
    session = MagicMock()
    responses = []
    for payload in payloads:
        response = MagicMock()
        response.json.return_value = payload
        response.raise_for_status.return_value = None
        responses.append(response)
    session.get.side_effect = responses
    return session


def test_bbox_is_parsed_as_floats():
    session = make_session([{"boundingbox": ["41.0", "43.8", "-9.3", "3.3"]}])
    bbox = OpenSkyNominatimAdapter(session).get_country_bbox("Spain")
    assert bbox == (41.0, 43.8, -9.3, 3.3)


def test_unknown_country_raises():
    session = make_session([])
    with pytest.raises(CountryNotFoundError):
        OpenSkyNominatimAdapter(session).get_country_bbox("Atlantis")


def test_null_states_returns_empty_list():
    session = make_session({"time": 1, "states": None})
    result = OpenSkyNominatimAdapter(session).get_aeroplanes_in_bbox((1, 2, 3, 4))
    assert result == []


def test_get_aeroplanes_combines_both_requests():
    session = make_session(
        [{"boundingbox": ["41.0", "43.8", "-9.3", "3.3"]}],
        {"time": 1, "states": [["4b1812"]]},
    )
    result = OpenSkyNominatimAdapter(session).get_aeroplanes("Spain")
    assert result == [["4b1812"]]
    assert session.get.call_count == 2


def test_network_error_is_wrapped_in_api_error():
    session = MagicMock()
    session.get.side_effect = requests.ConnectionError("нет связи")
    with pytest.raises(APIError):
        OpenSkyNominatimAdapter(session).get_country_bbox("Spain")


def test_country_not_found_is_api_error():
    assert issubclass(CountryNotFoundError, APIError)
