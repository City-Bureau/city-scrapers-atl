from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import BOARD
from city_scrapers_core.utils import file_response
from freezegun import freeze_time
from scrapy.http import HtmlResponse, Request

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
        url="https://citycouncil.atlantaga.gov/other/events/public-meetings/-curm-6/-cury-2025",
    )


@pytest.fixture
def detail_response():
    with open(
        join(dirname(__file__), "files", "atl_water_and_sewer_appeals_board_detail.html"),
        encoding="utf-8",
    ) as f:
        body = f.read()
    return HtmlResponse(
        url="https://citycouncil.atlantaga.gov/Home/Components/Calendar/Event/11129/165?curm=6&cury=2025",
        body=body.encode("utf-8"),
        encoding="utf-8",
        request=Request(
            url="https://citycouncil.atlantaga.gov/Home/Components/Calendar/Event/11129/165?curm=6&cury=2025",
            meta={"title": "Watershed Water and Sewer Appeals Board"},
        ),
    )


@pytest.fixture
def parsed_items(spider, detail_response):
    freezer = freeze_time("2026-04-15")
    freezer.start()
    items = list(spider._parse_detail(detail_response))
    freezer.stop()
    return items


@pytest.fixture
def detail_response_2026():
    with open(
        join(dirname(__file__), "files", "atl_water_and_sewer_appeals_board_detail_2026.html"),
        encoding="utf-8",
    ) as f:
        body = f.read()
    return HtmlResponse(
        url="https://citycouncil.atlantaga.gov/Home/Components/Calendar/Event/12243/165?curm=4&cury=2026",
        body=body.encode("utf-8"),
        encoding="utf-8",
        request=Request(
            url="https://citycouncil.atlantaga.gov/Home/Components/Calendar/Event/12243/165?curm=4&cury=2026",
            meta={"title": "Water and Sewer Appeals Board"},
        ),
    )


@pytest.fixture
def parsed_items_2026(spider, detail_response_2026):
    freezer = freeze_time("2026-04-15")
    freezer.start()
    items = list(spider._parse_detail(detail_response_2026))
    freezer.stop()
    return items


def test_listing_yields_two_requests(spider, listing_response):
    requests = list(spider.parse(listing_response))
    assert len(requests) == 2
    assert "11129/165" in requests[0].url
    assert "12243/165" in requests[1].url


def test_count(parsed_items):
    assert len(parsed_items) == 1


def test_title(parsed_items):
    assert parsed_items[0]["title"] == "Watershed Water and Sewer Appeals Board"


def test_description(parsed_items):
    assert parsed_items[0]["description"] == ""


def test_start(parsed_items):
    assert parsed_items[0]["start"] == datetime(2025, 6, 30, 16, 0)


def test_end(parsed_items):
    assert parsed_items[0]["end"] == datetime(2025, 6, 30, 18, 30)


def test_time_notes(parsed_items):
    assert parsed_items[0]["time_notes"] == ""


def test_classification(parsed_items):
    assert parsed_items[0]["classification"] == BOARD


def test_status(parsed_items):
    assert parsed_items[0]["status"] == "passed"


def test_location(parsed_items):
    assert parsed_items[0]["location"] == {
        "address": "72 Marietta ST, Atlanta, GA 30303",
        "name": "Main Floor, Auditorium (Room 215)",
    }


def test_source(parsed_items):
    assert parsed_items[0]["source"] == "https://citycouncil.atlantaga.gov/Home/Components/Calendar/Event/11129/165?curm=6&cury=2025"


def test_links(parsed_items):
    assert parsed_items[0]["links"] == [
        {"href": "https://citycouncil.atlantaga.gov/Home/Components/Calendar/Event/11129/165?curm=6&cury=2025", "title": "Agenda"}
    ]


def test_all_day(parsed_items):
    assert parsed_items[0]["all_day"] is False


def test_2026_title(parsed_items_2026):
    assert parsed_items_2026[0]["title"] == "Water and Sewer Appeals Board"


def test_2026_start(parsed_items_2026):
    assert parsed_items_2026[0]["start"] == datetime(2026, 4, 21, 15, 0)


def test_2026_end(parsed_items_2026):
    assert parsed_items_2026[0]["end"] == datetime(2026, 4, 21, 18, 30)


def test_2026_status(parsed_items_2026):
    assert parsed_items_2026[0]["status"] == "tentative"


def test_2026_classification(parsed_items_2026):
    assert parsed_items_2026[0]["classification"] == BOARD


def test_2026_location(parsed_items_2026):
    assert parsed_items_2026[0]["location"] == {
        "address": "72 Marietta ST, Atlanta, GA 30303",
        "name": "Main Floor, Auditorium (Room 215)",
    }


def test_2026_source(parsed_items_2026):
    assert parsed_items_2026[0]["source"] == "https://citycouncil.atlantaga.gov/Home/Components/Calendar/Event/12243/165?curm=4&cury=2026"


def test_2026_links(parsed_items_2026):
    assert parsed_items_2026[0]["links"] == [
        {"href": "https://citycouncil.atlantaga.gov/Home/Components/Calendar/Event/12243/165?curm=4&cury=2026", "title": "Agenda"}
    ]


def test_2026_all_day(parsed_items_2026):
    assert parsed_items_2026[0]["all_day"] is False
