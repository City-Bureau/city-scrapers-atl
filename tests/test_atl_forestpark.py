from datetime import datetime
from os.path import dirname, join

import pytest
from city_scrapers_core.constants import CITY_COUNCIL, NOT_CLASSIFIED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.atl_forestpark import ForestParkSpider

test_response = file_response(
    join(dirname(__file__), "files", "atl_forestpark.html"),
    url="https://www.forestparkga.gov/meetings",
)
spider = ForestParkSpider()

freezer = freeze_time("2022-10-18")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "City Council Regular Session"


# def test_description():
#     assert parsed_items[0]["description"] == "EXPECTED DESCRIPTION"


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 11, 7, 19, 0)


# def test_end():
#     assert parsed_items[0]["end"] == datetime(2019, 1, 1, 0, 0)


# def test_time_notes():
#     assert parsed_items[0]["time_notes"] == "EXPECTED TIME NOTES"


def test_id():
    assert (
        parsed_items[0]["id"]
        == "atl_forestpark/202211071900/x/city_council_regular_session"
    )
    assert (
        parsed_items[2]["id"]
        == "atl_forestpark/202210271815/x/urban_redevelopment_authority_regular_meeting"
    )


def test_status():
    assert parsed_items[0]["status"] == "tentative"
    assert parsed_items[2]["status"] == "tentative"


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "Forest Park City Council",
        "address": "745 Forest Parkway, Forest Park, GA 30297",
    }


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://www.forestparkga.gov/citycouncil/page/city-council-regular-session-35"  # noqa
    )
    assert (
        parsed_items[2]["source"]
        == "https://www.forestparkga.gov/bc-ura/page/urban-redevelopment-authority-regular-meeting-17"  # noqa
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://www.forestparkga.gov/citycouncil/page/city-council-regular-session-35",  # noqa
            "title": "View",
        }
    ]
    assert parsed_items[2]["links"] == [
        {
            "href": "https://www.forestparkga.gov/bc-ura/page/urban-redevelopment-authority-regular-meeting-17",  # noqa
            "title": "View",
        }
    ]


def test_classification():
    assert parsed_items[0]["classification"] == CITY_COUNCIL
    assert parsed_items[2]["classification"] == NOT_CLASSIFIED


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
