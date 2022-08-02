from datetime import datetime
from os.path import dirname, join

from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.atl_city_council import AtlCityCouncilSpider

test_response = file_response(
    join(dirname(__file__), "files", "atl_city_council.html"),
    url="https://citycouncil.atlantaga.gov/standing-committees/meeting-agendas/agenda",
)
spider = AtlCityCouncilSpider()

freezer = freeze_time("2022-08-01")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "EXPECTED TITLE"


def test_description():
    assert parsed_items[0]["description"] == "EXPECTED TITLE"


def test_start():
    assert parsed_items[0]["start"] == datetime(2019, 1, 1, 0, 0)


def test_links():
    assert parsed_items[0]["links"] == [
        {"href": "EXPECTED HREF", "title": "EXPECTED TITLE"}
    ]
