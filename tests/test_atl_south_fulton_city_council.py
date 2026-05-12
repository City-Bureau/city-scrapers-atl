from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import CITY_COUNCIL, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.atl_south_fulton_city_council import (
    AtlSouthFultonCityCouncilSpider,
)

atl_south_fulton_city_council_meetings = file_response(
    join(dirname(__file__), "files", "atl_south_fulton_city_council_meetings.json"),
    url="https://southfultonga.api.civicclerk.com/v1/Events?$filter=startDateTime+ge+2026-04-16+and+startDateTime+le+2027-04-16+and+categoryId+in+(26)",  # noqa
)


@pytest.fixture
def spider():
    return AtlSouthFultonCityCouncilSpider()


@pytest.fixture
def parsed_items(spider):
    with freeze_time("2026-04-16"):
        return [item for item in spider.parse(atl_south_fulton_city_council_meetings)]


def test_count(parsed_items):
    assert len(parsed_items) == 16


def test_title(parsed_items):
    assert parsed_items[0]["title"] == "Alcohol License and Zoning Public Hearings"


def test_description(parsed_items):
    assert parsed_items[0]["description"] == ""


def test_start(parsed_items):
    assert parsed_items[0]["start"] == datetime(2026, 4, 15, 17, 0)


def test_end(parsed_items):
    assert parsed_items[0]["end"] is None


def test_time_notes(parsed_items):
    assert parsed_items[0]["time_notes"] == ""


def test_id(parsed_items):
    assert (
        parsed_items[0]["id"]
        == "atl_south_fulton_city_council/202604151700/x/alcohol_license_and_zoning_public_hearings"  # noqa
    )


def test_status(parsed_items):
    assert parsed_items[0]["status"] == PASSED


def test_location(parsed_items):
    assert parsed_items[0]["location"] == {
        "name": "South Fulton City Hall",
        "address": "5440 Fulton Industrial Blvd South Fulton, Georgia, 30336",
    }


def test_source(parsed_items):
    assert (
        parsed_items[0]["source"]
        == "https://southfultonga.portal.civicclerk.com/event/1744"  # noqa
    )


def test_links(parsed_items):
    assert parsed_items[0]["links"] == [
        {
            "title": "Agenda",
            "href": "https://southfultonga.portal.civicclerk.com/event/1744/files/agenda/2261",  # noqa
        },
        {
            "title": "Agenda Packet",
            "href": "https://southfultonga.portal.civicclerk.com/event/1744/files/agenda/2262",  # noqa
        },
    ]


def test_classification(parsed_items):
    assert parsed_items[0]["classification"] == CITY_COUNCIL
