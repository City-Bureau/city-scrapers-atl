from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.atl_crb import AtlCrbSpider

test_response = file_response(
    join(dirname(__file__), "files", "atl_crb.html"),
    url="https://acrbgov.org/",
)
spider = AtlCrbSpider()

freezer = freeze_time("2022-08-10")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()

def test_total():
    assert len(parsed_items) == 4

def test_title():
    assert parsed_items[0]["title"] == "ACRB Meeting on September 8, 2022"

@pytest.mark.parametrize("item", parsed_items)
def test_description(item):
    assert item["description"] == "The ACRB usually meets every second Thursday of each month at 6:30 p.m. at Atlanta City Hall, 55 Trinity Avenue, SW, Second Floor, in Committee Room One."

def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 9, 8, 18, 30)

@pytest.mark.parametrize("item", parsed_items)
def test_location(item):
    assert item["location"] == {
        "name": "Atlanta City Hall",
        "address": "55 Trinity Avenue SW, Second Floor Atrium, Committee Room One, Atlanta, GA 30303"
    }

@pytest.mark.parametrize("item", parsed_items)
def test_links(item):
    assert item["links"] == [{
      "href": "https://www.youtube.com/channel/UCl_oXkXkPj6t9RoAgUKiYuQ",
      "title": "Watch Board Meetings"
    }]


@pytest.mark.parametrize("item", parsed_items)
def test_classification(item):
    assert item["classification"] == NOT_CLASSIFIED

