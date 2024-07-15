from datetime import datetime
from os.path import dirname, join

from city_scrapers_core.constants import BOARD
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.atl_dekalb_county_boe import AtlDekalbCountyBoeSpider  # noqa

test_response = file_response(
    join(dirname(__file__), "files", "atl_dekalb_county_boe.json"),
    url="https://www.dekalbschoolsga.org/board-of-education/board-meetings/",
)

spider = AtlDekalbCountyBoeSpider()

freezer = freeze_time("2024-07-15")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]
parsed_item = parsed_items[0]
freezer.stop()


def test_len():
    assert len(parsed_items) == 49


def test_title():
    assert parsed_item["title"] == "Audit Committee Meeting"


def test_description():
    assert parsed_item["description"] == ""


def test_start():
    assert parsed_item["start"] == datetime(2024, 7, 11, 13, 0)


def test_end():
    assert parsed_item["end"] is None


def test_id():
    assert (
        parsed_item["id"]
        == "atl_dekalb_county_boe/202407111300/x/audit_committee_meeting"
    )


def test_status():
    assert parsed_item["status"] == "passed"


def test_location():
    assert parsed_item["location"] == {
        "name": "Board Office Conference Room, Robert R. Freeman Administrative Complex",  # noqa
        "address": "1701 Mountain Industrial Boulevard Stone Mountain, Georgia 30083",  # noqa
    }


def test_source():
    assert (
        parsed_item["source"]
        == "https://simbli.eboardsolutions.com/SB_Meetings/SB_MeetingListing.aspx?S=4054"  # noqa
    )


def test_links():
    assert (
        parsed_item["links"] == []
    )  # Assuming no links are provided based on your data


def test_classification():
    assert parsed_item["classification"] == BOARD


def test_all_day():
    assert (
        parsed_item["all_day"] is False
    )  # Based on the boolean value for all_day from the data row
