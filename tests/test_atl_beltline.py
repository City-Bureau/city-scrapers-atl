from datetime import datetime
from os.path import dirname, join

# import pytest
from city_scrapers_core.constants import BOARD
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.atl_beltline import AtlBeltlineSpider

test_response = file_response(
    join(dirname(__file__), "files", "atl_beltline.html"),
    url="https://beltline.org/wp-json/tribe/events/v1/events",
)
spider = AtlBeltlineSpider()

freezer = freeze_time("2022-08-11")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_total():
    assert len(parsed_items) == 3


def test_title():
    assert (
        parsed_items[0]["title"] == "Atlanta BeltLine, Inc. Board of Directors Meeting"
    )


def test_description():
    assert (
        parsed_items[0]["description"]
        == """<p>This meeting of Atlanta BeltLine, Inc.’s Board of Directors """
        """will be held on Wednesday, August 10, 2022.</p>
<p>To submit public comment, email ceo@atlbeltline.org by Wednesday, """
        """August 10 at 8:30 am. Please include your full name, """
        """telephone number, email and area of residence.</p>
<p>Board of Directors meetings are held the second """
        """Wednesday of every month at 8:30 a.m.</p>"""
    )


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 8, 10, 8, 30)


def test_end():
    assert parsed_items[0]["end"] == datetime(2022, 8, 10, 10, 0)


def test_id():
    assert (
        parsed_items[0]["id"]
        == "atl_beltline/202208100830/x/atlanta_beltline_inc_board_of_directors_meeting"
    )


def test_status():
    assert parsed_items[0]["status"] == "passed"


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Virtual",
        "address": "https://beltline.org/venue/virtual/",
    }


def test_source():
    assert (
        parsed_items[0]["source"] == "https://beltline.org/event/"
        "atlanta-beltline-inc-board-of-directors-meeting-11/"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://beltline.org/organizer/atlanta-beltline-inc/",
            "title": "Atlanta BeltLine, Inc.",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == BOARD


# @pytest.mark.parametrize("item", parsed_items)
# def test_all_day(item):
#     assert item["all_day"] is False
