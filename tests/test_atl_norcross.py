from datetime import datetime
from os.path import dirname, join

from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.atl_norcross import AtlNorcrossSpider

test_response = file_response(
    join(dirname(__file__), "files", "atl_norcross.html"),
    url="http://norcrossga.iqm2.com/Citizens/default.aspx",
)
spider = AtlNorcrossSpider()

freezer = freeze_time("2022-08-30")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Mayor and Council - Regular Meeting"


def test_description():
    assert "Regular Meeting" in parsed_items[0]["description"]


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 9, 6, 18, 30)


def test_source():
    assert (
        parsed_items[0]["source"] == "http://norcrossga.iqm2.com/Citizens/default.aspx"
    )


def test_links():
    assert parsed_items[0]["links"] == []
