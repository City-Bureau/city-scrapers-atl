from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.dafc import DafcSpider

test_response = file_response(
    join(dirname(__file__), "files", "dafc.html"),
    url="https://www.developfultoncounty.com/meetings-and-minutes.php",
)
spider = DafcSpider()

freezer = freeze_time("2022-09-09")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_len():
    assert len(parsed_items) == 37


def test_title():
    assert (
        parsed_items[0]["title"]
        == "Development Authority of Fulton County JDAMA Meeting"
    )


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 1, 14, 10, 0)


def test_end():
    assert parsed_items[0]["end"] == datetime(2022, 1, 14, 12, 0)


def test_time_notes():
    assert (
        parsed_items[0]["time_notes"]
        == "End time seems to vary between 30 minutes to 2 hours after start"
    )


def test_id():
    assert (
        parsed_items[0]["id"]
        == "dafc/202201141000/x/development_authority_of_fulton_county_jdama_meeting"
    )


def test_status():
    assert parsed_items[0]["status"] == "passed"
    assert parsed_items[10]["status"] == "cancelled"
    assert parsed_items[28]["status"] == "tentative"


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Fulton County Government Administration Building",
        "address": "141 Pryor Street SW, 2nd Floor Conference Room, Suite 2052 (Peachtree Level), Atlanta, Georgia 30303",  # noqa
    }


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://www.developfultoncounty.com/meetings-and-minutes.php"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "mailto:doris.coleman@fultoncountyga.gov",
            "title": "Contact Doris M. Coleman for questions regarding meetings",
        },
        {
            "href": "https://www.developfultoncounty.com/meetings-and-minutes_6_4028117411.pdf",  # noqa
            "title": "Preliminary Agenda & Fact Sheet",
        },
        {
            "href": "https://www.developfultoncounty.com/meetings-and-minutes_13_1979264317.pdf",  # noqa
            "title": "Resolutions",
        },
        {
            "href": "https://www.developfultoncounty.com/meetings-and-minutes_13_3276803833.pdf",  # noqa
            "title": "Agenda",
        },
        {
            "href": "https://www.developfultoncounty.com/meetings-and-minutes_14_151474028.pdf",  # noqa
            "title": "Actions",
        },
        {
            "href": "https://www.developfultoncounty.com/meetings-and-minutes_23_3608142943.pdf",  # noqa
            "title": "Minutes",
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == NOT_CLASSIFIED


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
