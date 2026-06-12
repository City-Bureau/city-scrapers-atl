from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.atl_water_and_sewer_appeals_board import (
    AtlWaterAndSewerAppealsBoardSpider,
)


@pytest.fixture
def spider():
    return AtlWaterAndSewerAppealsBoardSpider()


@pytest.fixture
def listing_response():
    return file_response(
        join(dirname(__file__), "files", "atl_water_and_sewer_appeals_board.html"),
        url="https://citycouncil.atlantaga.gov/other/events/public-meetings/-curm-6/-cury-2026",  # noqa
    )


@pytest.fixture
def parsed_items(spider, listing_response):
    freezer = freeze_time("2026-06-10")
    freezer.start()
    items = list(spider.parse(listing_response))
    freezer.stop()
    return items


def test_count(parsed_items):
    assert len(parsed_items) == 4


def test_title(parsed_items):
    assert parsed_items[0]["title"] == "Water and Sewer Appeals Board"


def test_description(parsed_items):
    assert parsed_items[0]["description"] == ""


def test_start(parsed_items):
    assert parsed_items[0]["start"] == datetime(2026, 6, 1, 15, 0)


def test_end(parsed_items):
    assert parsed_items[0]["end"] is None


def test_time_notes(parsed_items):
    assert (
        parsed_items[0]["time_notes"] == "See attachments for accurate location details"
    )


def test_classification(parsed_items):
    assert parsed_items[0]["classification"] == BOARD


def test_status(parsed_items):
    assert parsed_items[0]["status"] == "passed"


def test_location(parsed_items):
    assert parsed_items[0]["location"] == {
        "address": "",
        "name": "",
    }


def test_source(parsed_items):
    assert (
        parsed_items[0]["source"]
        == "https://citycouncil.atlantaga.gov/Home/Components/Calendar/Event/12351/165?curm=6&cury=2026"  # noqa
    )


def test_links(parsed_items):
    assert parsed_items[0]["links"] == [
        {
            "href": "https://citycouncil.atlantaga.gov/Home/Components/Calendar/Event/12351/165?curm=6&cury=2026",  # noqa
            "title": "Agenda",
        }
    ]


def test_all_day(parsed_items):
    assert parsed_items[0]["all_day"] is False


def test_id(parsed_items):
    assert (
        parsed_items[0]["id"]
        == "atl_water_and_sewer_appeals_board/202606011500/x/water_and_sewer_appeals_board"  # noqa
    )
