from datetime import datetime
from os.path import dirname, join

from city_scrapers_core.constants import NOT_CLASSIFIED, TENTATIVE
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.atl_cobb_county_elections import (  # noqa
    AtlCobbCountyElectionsSpider,
)

test_response = file_response(
    join(dirname(__file__), "files", "atl_cobb_county_elections.html"),
    url="https://www.cobbcounty.org/elections/events",
)
spider = AtlCobbCountyElectionsSpider()

freezer = freeze_time("2024-04-01")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert (
        parsed_items[0]["title"]
        == "COBB COUNTY BOARD OF ELECTIONS & REGISTRATION MEETING"
    )


def test_start():
    assert parsed_items[0]["start"] == datetime(2024, 5, 21, 19, 0)


def test_end():
    assert parsed_items[0]["end"] is None


def test_id():
    assert (
        parsed_items[0]["id"]
        == "atl_cobb_county_elections/202405211900/x/cobb_county_board_of_elections_registration_meeting"  # noqa
    )


def test_links():
    expected_links = [
        {
            "href": "https://www.cobbcounty.org/events/cobb-county-board-elections-registration-meeting-3",  # noqa
            "title": "Event Details",
        }
    ]
    assert parsed_items[0]["links"] == expected_links


def test_location():
    expected_location = {"address": "", "name": "TBD"}
    assert parsed_items[0]["location"] == expected_location


def test_source():
    assert (
        parsed_items[0]["source"] == "https://www.cobbcounty.org/elections/events"
    )  # noqa


def test_classification():
    assert parsed_items[0]["classification"] == NOT_CLASSIFIED


def test_description():
    assert parsed_items[0]["description"] == ""


def test_all_day():
    assert parsed_items[0]["all_day"] is False


def test_status():
    assert parsed_items[0]["status"] == TENTATIVE


def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""
