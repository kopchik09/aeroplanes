import unittest
from unittest.mock import MagicMock

from src.api.adapters import CountryNotFoundError, OpenSkyNominatimAdapter


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


class TestOpenSkyNominatimAdapter(unittest.TestCase):
    def test_bbox_is_parsed_as_floats(self):
        session = make_session([{"boundingbox": ["41.0", "43.8", "-9.3", "3.3"]}])
        bbox = OpenSkyNominatimAdapter(session).get_country_bbox("Spain")
        self.assertEqual(bbox, (41.0, 43.8, -9.3, 3.3))

    def test_unknown_country_raises(self):
        session = make_session([])
        with self.assertRaises(CountryNotFoundError):
            OpenSkyNominatimAdapter(session).get_country_bbox("Atlantis")

    def test_null_states_returns_empty_list(self):
        session = make_session({"time": 1, "states": None})
        result = OpenSkyNominatimAdapter(session).get_aeroplanes_in_bbox((1, 2, 3, 4))
        self.assertEqual(result, [])

    def test_get_aeroplanes_combines_both_requests(self):
        session = make_session(
            [{"boundingbox": ["41.0", "43.8", "-9.3", "3.3"]}],
            {"time": 1, "states": [["4b1812"]]},
        )
        result = OpenSkyNominatimAdapter(session).get_aeroplanes("Spain")
        self.assertEqual(result, [["4b1812"]])
        self.assertEqual(session.get.call_count, 2)


if __name__ == "__main__":
    unittest.main()