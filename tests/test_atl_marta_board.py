from datetime import datetime
from os.path import dirname, join

from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.atl_marta_board import AtlMartaBoardSpider

test_response = file_response(
    join(dirname(__file__), "files", "atl_marta_board.html"),
    url="https://www.itsmarta.com/meeting-schedule.aspx",
)
spider = AtlMartaBoardSpider()

freezer = freeze_time("2022-08-20")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    assert len(parsed_items) == 24


def test_title():
    assert parsed_items[0]["title"] == "Board Working Session"


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 1, 13, 12, 0)
