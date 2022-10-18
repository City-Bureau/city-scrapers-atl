from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.atl_fdha import AtlFdhaSpider

test_response = file_response(
    join(dirname(__file__), "files", "atl_fdha.html"),
    url="https://thefdha.org/wp-json/tribe/events/v1/events",
)
spider = AtlFdhaSpider()

freezer = freeze_time("2022-09-21")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_len():
    assert len(parsed_items) == 5


def test_title():
    assert parsed_items[0]["title"] == "3Q Regular Full Board Meeting (2022)"


def test_description():
    assert (
        parsed_items[0]["description"]
        == '<p data-pm-slice="1 1 []">The Fulton Dekalb Hospital Authority will hold a regular Full Board Meeting Tues., Nov. 15th @ 5:30 pm. The meeting will take place in the Sandra Holliday Conference Room at the FDHA Office | 145 Edgewood Ave., 2nd Floor | Atlanta, GA 30303</p>'  # noqa
    )


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 11, 15, 17, 30)


def test_end():
    assert parsed_items[0]["end"] == datetime(2022, 11, 15, 17, 30)


def test_id():
    assert (
        parsed_items[0]["id"]
        == "atl_fdha/202211151730/x/3q_regular_full_board_meeting_2022_"
    )


def test_status():
    assert parsed_items[0]["status"] == "tentative"


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "The Fulton-DeKalb Hospital Authority",
        "address": "145 Edgewood Ave., 2nd Floor,, Atlanta, GA 30303",
    }


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://thefdha.org/event/3q-regular-full-board-meeting/"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://thefdha.org/organizer/the-fulton-dekalb-hospital-authority/",  # noqa
            "title": "The Fulton Dekalb Hospital Authority",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == BOARD


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
