from datetime import datetime
from os.path import dirname, join

import pytest  # noqa
from city_scrapers_core.constants import COMMITTEE, PASSED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.atl_boe import AtlBoeSpider

test_response = file_response(
    join(dirname(__file__), "files", "atl_boe.json"),
    url="https://awsapieast1-prod23.schoolwires.com/REST/api/v4/CalendarEvents/GetEvents/17299?StartDate=2024-04-10&EndDate=2024-08-08&ModuleInstanceFilter=&CategoryFilter=&IsDBStreamAndShowAll=true",  # noqa
)

spider = AtlBoeSpider()

freezer = freeze_time("2024-05-10")
freezer.start()

parsed_items = [item for item in spider.parse_events(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Oglethorpe Renaming Committee Meeting"


def test_start():
    assert parsed_items[0]["start"] == datetime(2024, 4, 11, 17, 30)


def test_end():
    assert parsed_items[0]["end"] == datetime(2024, 4, 11, 19, 0)


def test_id():
    assert (
        parsed_items[0]["id"]
        == "atl_boe/202404111730/x/oglethorpe_renaming_committee_meeting"
    )


def test_status():
    assert parsed_items[0]["status"] == PASSED


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Atlanta Public Schools",
        "address": "130 Trinity Ave SW, Atlanta, GA 30303",
    }


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://awsapieast1-prod23.schoolwires.com/REST/api/v4/CalendarEvents/GetEvents/17299?StartDate=2024-04-10&EndDate=2024-08-08&ModuleInstanceFilter=&CategoryFilter=&IsDBStreamAndShowAll=true"  # noqa
    )


def test_links():
    assert parsed_items[0]["links"] == AtlBoeSpider.default_links


def test_classification():
    assert parsed_items[0]["classification"] == COMMITTEE
