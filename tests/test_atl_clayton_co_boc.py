from datetime import datetime
from os.path import dirname, join

from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.atl_clayton_co_boc import AtlClaytonCoBocSpider

test_response = file_response(
    join(dirname(__file__), "files", "atl_clayton_co_boc.html"),
    url="http://claytoncountyga.iqm2.com/Citizens/Calendar.aspx",
)
spider = AtlClaytonCoBocSpider()

freezer = freeze_time("2022-08-30")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert (
        parsed_items[0]["title"] == "Board of Commissioners - Regular Business Meeting"
    )


def test_description():
    assert "Regular Business Meeting" in parsed_items[0]["description"]


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 1, 4, 18, 30)


def test_source():
    assert (
        parsed_items[0]["source"]
        == "http://claytoncountyga.iqm2.com/Citizens/Calendar.aspx"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://claytoncountyga.iqm2.com/FileOpen.aspx?Type=14&ID=1303&Inline=True",  # noqa
            "title": "Agenda",
        },
        {
            "href": "https://claytoncountyga.iqm2.com/FileOpen.aspx?Type=1&ID=1303&Inline=True",  # noqa
            "title": "Agenda Packet",
        },
        {
            "href": "https://claytoncountyga.iqm2.com/FileOpen.aspx?Type=15&ID=1302&Inline=True",  # noqa
            "title": "Summary",
        },
        {
            "href": "https://claytoncountyga.iqm2.com/FileOpen.aspx?Type=12&ID=1302&Inline=True",  # noqa
            "title": "Minutes",
        },
    ]
