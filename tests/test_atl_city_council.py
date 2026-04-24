from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.atl_city_council import (
    AtlCityCouncilCDHSpider,
    AtlCityCouncilCOCSpider,
    AtlCityCouncilFinSpider,
    AtlCityCouncilSafetySpider,
    AtlCityCouncilSpider,
    AtlCityCouncilTransportationSpider,
    AtlCityCouncilUtilSpider,
    AtlCityCouncilZoningSpider,
)

test_response = file_response(
    join(dirname(__file__), "files", "atl_city_council.html"),
    url="https://citycouncil.atlantaga.gov/",
)
spider = AtlCityCouncilSpider()

freezer = freeze_time("2026-01-01")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Atlanta City Council - Regular Meeting"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2026, 1, 5, 13, 0)


def test_classification():
    from city_scrapers_core.constants import CITY_COUNCIL

    assert parsed_items[0]["classification"] == CITY_COUNCIL


def test_location():
    assert (
        parsed_items[0]["location"]["name"]
        == "Marvin S. Arrington, Sr. Council Chamber"
    )
    assert "55 Trinity Avenue" in parsed_items[0]["location"]["address"]


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://atlantacityga.iqm2.com/Citizens/FileOpen.aspx?Type=14&ID=3810&Inline=True",  # noqa
            "title": "Agenda",
        },
        {
            "href": "https://atlantacityga.iqm2.com/Citizens/FileOpen.aspx?Type=1&ID=3810&Inline=True",  # noqa
            "title": "Agenda Packet",
        },
        {
            "href": "https://atlantacityga.iqm2.com/Citizens/FileOpen.aspx?Type=15&ID=4011&Inline=True",  # noqa
            "title": "Minutes",
        },
        {
            "href": "https://atlantacityga.iqm2.com/Citizens/FileOpen.aspx?Type=12&ID=4011&Inline=True",  # noqa
            "title": "Minutes Packet",
        },
        {
            "href": "https://atlantacityga.iqm2.com/Citizens/SplitView.aspx?Mode=Video&MeetingID=4098&Format=Minutes",  # noqa
            "title": "Video",
        },
    ]


# The number of meetings for 2026 year
@pytest.mark.parametrize(
    "cls,expected",
    [
        (AtlCityCouncilSpider, 22),
        (AtlCityCouncilFinSpider, 21),
        (AtlCityCouncilUtilSpider, 21),
        (AtlCityCouncilCOCSpider, 20),
        (AtlCityCouncilCDHSpider, 21),
        (AtlCityCouncilSafetySpider, 20),
        (AtlCityCouncilTransportationSpider, 18),
        (AtlCityCouncilZoningSpider, 21),
    ],
)
def test_sub_spider(cls, expected):
    spider = cls()
    parsed_items = list(spider.parse(test_response))
    assert len(parsed_items) == expected
