from datetime import datetime
from os.path import dirname, join

import pytest
import scrapy
from city_scrapers_core.constants import BOARD
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.atl_clayton_co_boc import AtlClaytonCoBocSpider


@pytest.fixture(scope="module")
def spider():
    return AtlClaytonCoBocSpider()


@pytest.fixture(scope="module")
def upcoming_meetings_data():
    response = file_response(
        join(
            dirname(__file__),
            "files",
            "atl_clayton_co_boc_upcoming_meetings.json",
        ),
        url="https://claytoncountyga.primegov.com/api/v2/PublicPortal/ListUpcomingMeetings",  # noqa
    )
    return response


@pytest.fixture(scope="module")
def archived_meetings_data(upcoming_meetings_data):
    url = "https://claytoncountyga.primegov.com/api/v2/PublicPortal/ListArchivedMeetings?year=2026"  # noqa

    request = scrapy.Request(
        url=url,
        meta={
            "upcoming_meetings": upcoming_meetings_data,
        },
    )

    response = file_response(
        join(
            dirname(__file__),
            "files",
            "atl_clayton_co_boc_archived_meetings.json",
        ),
        url=url,
    )

    response.request = request

    return response


@pytest.fixture(scope="module")
def parsed_items(spider, archived_meetings_data):
    with freeze_time("2026-04-27"):
        items = list(spider.parse(archived_meetings_data))

    return items


def test_count(parsed_items):
    assert len(parsed_items) == 20


def test_title(parsed_items):
    assert parsed_items[0]["title"] == "Regular Business Meeting"


def test_description(parsed_items):
    assert parsed_items[0]["description"] == ""


def test_start(parsed_items):
    assert parsed_items[0]["start"] == datetime(2026, 1, 6, 18, 0)


def test_end(parsed_items):
    assert parsed_items[0]["end"] is None


def test_time_notes(parsed_items):
    assert (
        parsed_items[0]["time_notes"]
        == "For meeting's details, please refer to the source URL."
    )


def test_id(parsed_items):
    assert (
        parsed_items[0]["id"]
        == "atl_clayton_co_boc/202601061800/x/regular_business_meeting"
    )


def test_status(parsed_items):
    assert parsed_items[0]["status"] == "passed"


def test_location(parsed_items):
    assert parsed_items[0]["location"] == {
        "name": "",
        "address": "",
    }


def test_source(parsed_items):
    assert (
        parsed_items[0]["source"]
        == "https://claytoncountyga.primegov.com/public/portal?fromiframe=true"
    )


def test_links(parsed_items):
    assert parsed_items[0]["links"] == [
        {
            "title": "Summary Minutes",
            "href": "https://claytoncountyga.primegov.com/Public/CompiledDocument?meetingTemplateId=4414&compileOutputType=1",  # noqa
        },
        {
            "title": "Minutes",
            "href": "https://claytoncountyga.primegov.com/Public/CompiledDocument?meetingTemplateId=4410&compileOutputType=1",  # noqa
        },
        {
            "title": "Video",
            "href": "http://claytoncountyga.granicus.com/MediaPlayer.php?clip_id=34",
        },
    ]


def test_classification(parsed_items):
    assert parsed_items[0]["classification"] == BOARD


def test_all_day(parsed_items):
    for item in parsed_items:
        assert item["all_day"] is False
