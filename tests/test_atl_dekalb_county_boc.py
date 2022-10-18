from datetime import datetime
from os import listdir
from os.path import basename, dirname, join, splitext

import pytest
from city_scrapers_core.constants import CITY_COUNCIL
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.atl_dekalb_county_boc import AtlDekalbCountyBocSpider

test_response = file_response(
    join(dirname(__file__), "files", "atl_dekalb_county_boc.html"),
    url="https://www.dekalbcountyga.gov/meeting-calendar",
)

spider = AtlDekalbCountyBocSpider()

freezer = freeze_time("2022-09-08")
freezer.start()

meeting_requests = [item for item in spider.parse(test_response)]

requests_url_root = "https://www.dekalbcountyga.gov/event-popup"
requests_dir_root = join(dirname(__file__), "files", "atl_dekalb_county_boc_requests")
meeting_responses = [
    file_response(
        join(requests_dir_root, item),
        url=join(requests_url_root, splitext(basename(item))[0]),
    )
    for item in listdir(requests_dir_root)
    if "html" in item
]

for response in meeting_responses:
    for request in meeting_requests:
        if response.url == request.url:
            response.request = request
            break

parsed_items = [
    item for response in meeting_responses for item in spider._parse_meeting(response)
]

parsed_items.sort(key=lambda item: item["start"])

freezer.stop()


def test_item_len():
    assert len(parsed_items) == 14


def test_title():
    assert (
        parsed_items[0]["title"] == "Board of Commissioner’s Committee of the Whole"
    )  # noqa
    assert (
        parsed_items[7]["title"] == "Finance Audit and Budget Committee Committee"
    )  # noqa


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 9, 6, 9, 0)
    assert parsed_items[7]["start"] == datetime(2022, 9, 13, 15, 30)


def test_end():
    assert parsed_items[0]["end"] == datetime(2022, 9, 6, 11, 30)
    assert parsed_items[7]["end"] == datetime(2022, 9, 13, 17, 0)


def test_id():
    assert (
        parsed_items[0]["id"]
        == "atl_dekalb_county_boc/202209060900/x/board_of_commissioner_s_committee_of_the_whole"  # noqa
    )
    assert (
        parsed_items[7]["id"]
        == "atl_dekalb_county_boc/202209131530/x/finance_audit_and_budget_committee_committee"  # noqa
    )


def test_status():
    assert parsed_items[0]["status"] == "passed"
    assert parsed_items[7]["status"] == "tentative"


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://www.dekalbcountyga.gov/event-popup/1207800"
    )
    assert (
        parsed_items[7]["source"]
        == "https://www.dekalbcountyga.gov/event-popup/1207827"
    )


def test_links():
    assert parsed_items[0]["links"] == [
        {"href": "https://video.ibm.com/channel/dctv-channel-23", "title": "DCTV"},
        {
            "href": "https://www.dekalbcountyga.gov/board-commissioners/committee-whole-cow",  # noqa
            "title": "webpage",
        },
        {
            "href": "https://www.dekalbcountyga.gov/board-commissioners/public-participation",  # noqa
            "title": "Public Participation",
        },
    ]


def test_classification():
    assert parsed_items[0]["classification"] == CITY_COUNCIL


@pytest.mark.parametrize("item", parsed_items)
def test_all_day(item):
    assert item["all_day"] is False
