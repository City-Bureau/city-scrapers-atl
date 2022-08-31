from datetime import datetime
from os.path import dirname, join

from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.atl_cobb_county_elections import AtlCobbCountyElectionsSpider

test_response = file_response(
    join(dirname(__file__), "files", "atl_cobb_county_elections.html"),
    url="https://www.cobbcounty.org/elections/events",
)
spider = AtlCobbCountyElectionsSpider()

freezer = freeze_time("2022-08-30")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Labor Day Holiday"


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 9, 5, 8, 0)


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://www.cobbcounty.org/elections/events/labor-day-holiday-0"
    )
