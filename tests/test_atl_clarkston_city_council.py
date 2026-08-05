import json
from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import CITY_COUNCIL, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.atl_clarkston_city_council import (
    AtlClarkstonCityCouncilSpider,
)

atl_clarkston_city_council = file_response(
    join(dirname(__file__), "files", "atl_clarkston_city_council.json"),
    url="https://clarkstonga.api.civicclerk.com/v1/Events?$filter=startDateTime+ge+2026-04-28+and+startDateTime+le+2027-04-16+and+categoryId+in+(26)",  # noqa
)


def _strip_next_link(response):
    """
    parse() defers yielding Meetings until self._pending_requests hits 0, which only
    happens once there's no further pagination to follow.
    """
    data = json.loads(response.text)
    data.pop("@odata.nextLink", None)
    return response.replace(body=json.dumps(data).encode("utf-8"))


@pytest.fixture
def spider():
    return AtlClarkstonCityCouncilSpider()


@pytest.fixture
def parsed_items(spider):
    spider._raw_events = []
    spider._pending_requests = 1

    response = _strip_next_link(atl_clarkston_city_council)

    with freeze_time("2026-04-28"):
        results = list(spider.parse(response))

    return results


def test_count(parsed_items):
    assert len(parsed_items) == 15


def test_title(parsed_items):
    assert parsed_items[0]["title"] == "City Council Work Session"


def test_description(parsed_items):
    assert parsed_items[0]["description"] == ""


def test_time_notes(parsed_items):
    assert (
        parsed_items[0]["time_notes"]
        == "Please refer to the meeting attachments for more accurate meeting time and location."  # noqa
    )


def test_start(parsed_items):
    assert parsed_items[0]["start"] == datetime(2026, 4, 28, 19, 0)


def test_end(parsed_items):
    assert parsed_items[0]["end"] is None


def test_id(parsed_items):
    assert (
        parsed_items[0]["id"]
        == "atl_clarkston_city_council/202604281900/x/city_council_work_session"  # noqa
    )


def test_status(parsed_items):
    assert parsed_items[0]["status"] == TENTATIVE


def test_location(parsed_items):
    assert parsed_items[0]["location"] == {
        "name": "City Hall Municipal Building, Suite 120",
        "address": "736 Park North Blvd. Clarkston, GA, 30021",
    }


def test_source(parsed_items):
    assert (
        parsed_items[0]["source"]
        == "https://clarkstonga.portal.civicclerk.com/event/1089"  # noqa
    )


def test_links(parsed_items):
    assert parsed_items[0]["links"] == [
        {
            "title": "Video",
            "href": "https://clarkstonga.portal.civicclerk.com/event/1089/media",
        },
        {
            "title": "Agenda",
            "href": "https://clarkstonga.portal.civicclerk.com/event/1089/files/agenda/3533",  # noqa
        },
        {
            "title": "Agenda Packet",
            "href": "https://clarkstonga.portal.civicclerk.com/event/1089/files/agenda/3539",  # noqa
        },
    ]


def test_classification(parsed_items):
    assert parsed_items[0]["classification"] == CITY_COUNCIL
