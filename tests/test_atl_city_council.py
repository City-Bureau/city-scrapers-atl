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

freezer = freeze_time("2022-08-01")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert (
        parsed_items[0]["title"]
        == "Atlanta City Council - First Organizational Meeting"
    )


def test_description():
    assert "Status:\tClosed" in parsed_items[0]["description"]
    assert "Board:\tAtlanta City Council" in parsed_items[0]["description"]


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 1, 3, 13, 0)


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://atlantacityga.iqm2.com/FileOpen.aspx?Type=14&ID=3126&Inline=True",  # noqa
            "title": "Agenda",
        },
        {
            "href": "https://atlantacityga.iqm2.com/FileOpen.aspx?Type=1&ID=3126&Inline=True",  # noqa
            "title": "Agenda Packet",
        },
        {
            "href": "https://atlantacityga.iqm2.com/FileOpen.aspx?Type=15&ID=3322&Inline=True",  # noqa
            "title": "Minutes",
        },
        {
            "href": "https://atlantacityga.iqm2.com/FileOpen.aspx?Type=12&ID=3322&Inline=True",  # noqa
            "title": "Minutes Packet",
        },
    ]


@pytest.mark.parametrize(
    "cls,expected",
    [
        (AtlCityCouncilSpider, 23),
        (AtlCityCouncilFinSpider, 15),
        (AtlCityCouncilUtilSpider, 15),
        (AtlCityCouncilCOCSpider, 14),
        (AtlCityCouncilCDHSpider, 17),
        (AtlCityCouncilSafetySpider, 15),
        (AtlCityCouncilTransportationSpider, 15),
        (AtlCityCouncilZoningSpider, 16),
    ],
)
def test_sub_spider(cls, expected):
    spider = cls()
    parsed_items = list(spider.parse(test_response))
    assert len(parsed_items) == expected
