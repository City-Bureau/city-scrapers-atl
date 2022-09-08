from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import COMMISSION
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.atl_boe import AtlBoeSpider

test_response = file_response(
    join(dirname(__file__), "files", "atl_boe.html"),
    url="https://www.atlantapublicschools.us/apsboard",
)
spider = AtlBoeSpider()

freezer = freeze_time("2022-08-26")
freezer.start()

parsed_items = [item.meta["meeting"] for item in spider.parse(test_response)]

freezer.stop()


def test_length():
    assert len(parsed_items) == 5


def test_title():
    assert parsed_items[0]["title"] == "Accountability Commission Meeting"


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 8, 29, 10, 0)


def test_end():
    assert parsed_items[0]["end"] == datetime(2022, 8, 29, 11, 30)


def test_id():
    assert (
        parsed_items[0]["id"]
        == "atl_boe/202208291000/x/accountability_commission_meeting"
    )


def test_status():
    assert parsed_items[0]["status"] == "tentative"


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Center for Learning and Leadership",
        "address": "130 Trinity Avenue, Atlanta, GA 30303",
    }


def test_source():
    assert parsed_items[0]["source"] == "https://www.atlantapublicschools.us/apsboard"


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://www.atlantapublicschools.us/site/Default.aspx?PageID=17673&DomainID=3944#calendar17299/20220829/event/236419",  # noqa
            "title": "Meeting details",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == COMMISSION


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
