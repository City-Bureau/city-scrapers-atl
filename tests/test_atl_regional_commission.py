from datetime import datetime
from os.path import dirname, join

from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.atl_regional_commission import AtlRegionalCommissionSpider

test_response = file_response(
    join(dirname(__file__), "files", "atl_regional_commission.html"),
    url="https://atlantaregional.org/wp-json/tribe/events/v1/events",
)
spider = AtlRegionalCommissionSpider()

freezer = freeze_time("2022-08-30")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Transportation Coordinating Committee"


def test_description():
    assert parsed_items[0]["description"] == ""


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 9, 9, 9, 30)


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://atlantaregional.org/event/transportation-coordinating-committee-30/"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://atlantaregional.org/event/transportation-coordinating-committee-30/",  # noqa
            "title": "Event Website",
        }
    ]
