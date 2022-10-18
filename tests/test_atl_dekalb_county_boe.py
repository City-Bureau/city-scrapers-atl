from datetime import datetime
from os.path import dirname, join

from city_scrapers_core.constants import BOARD
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.atl_dekalb_county_boe import AtlDekalbCountyBoeSpider

test_response = file_response(
    join(dirname(__file__), "files", "atl_dekalb_county_boe.html"),
    url="https://www.dekalbschoolsga.org/board-of-education/board-meetings/",
)

meeting_response = file_response(
    join(dirname(__file__), "files", "atl_dekalb_county_boe_927.html"),
    url="https://www.dekalbschoolsga.org/event/board-of-education-meeting-21/?instance_id=927",  # noqa
)

spider = AtlDekalbCountyBoeSpider()

freezer = freeze_time("2022-09-21")
freezer.start()

requests = [item for item in spider.parse(test_response)]
meeting = [item for item in spider._parse_meeting_page(meeting_response)][0]

freezer.stop()


def test_len():
    assert len(requests) == 4


def test_title():
    assert meeting["title"] == "Board of Education Meeting"


def test_description():
    assert (
        meeting["description"]
        == "<p>All Business Meetings begin at 1:00pm (unless noticed for some other time), and will be held in the J. David Williamson Board Room in the Robert R. Freeman Administrative Complex, 1701 Mountain Industrial Boulevard, Stone Mountain, Georgia.</p>\n"  # noqa
        "<p>All Work Sessions begin at 1:00pm (unless noticed for some other time), and will be held in the J. David Williamson Board Room, in the Robert R. Freeman Administrative Complex, 1701 Mountain Industrial Boulevard, Stone Mountain, Georgia.</p>\n"  # noqa
        '<p>All meetings can be viewed on DeKalb Schools TV (DSTV) by going to: <a href="https://www.dekalbschoolsga.org/communications/dstv" target="_blank" rel="noopener">www.dekalbschoolsga.org/communications/dstv</a> or Comcast channel 24 (for Comcast subscribers in DeKalb County).</p>\n'  # noqa
        '<p>For more info, visit the <a href="https://simbli.eboardsolutions.com/Index.aspx?S=4054">Board of Education homepage</a>.</p>'  # noqa
    )


def test_start():
    assert meeting["start"] == datetime(2022, 11, 14, 0, 0)


def test_end():
    assert meeting["end"] is None


def test_id():
    assert (
        meeting["id"]
        == "atl_dekalb_county_boe/202211140000/x/board_of_education_meeting"
    )


def test_status():
    assert meeting["status"] == "tentative"


def test_location():
    assert meeting["location"] == {
        "name": "Robert R. Freeman Administrative & Instructional Complex",
        "address": "1701 Mountain Industrial Blvd, Stone Mountain, GA 30083, USA",
    }


def test_source():
    assert (
        meeting["source"]
        == "https://www.dekalbschoolsga.org/event/board-of-education-meeting-21/?instance_id=927"  # noqa
    )


def test_links():
    assert meeting["links"] == [
        {
            "href": "https://www.dekalbschoolsga.org/communications/dstv",
            "title": "DSTV (Comcast channel 24)",
        },
        {
            "href": "https://www.google.com/maps?f=q&hl=&source=embed&q=33.83259%2C-84.194653",  # noqa
            "title": "",
        },
        {
            "href": "https://simbli.eboardsolutions.com/index.aspx?s=4054",
            "title": "Event website",
        },
        {
            "href": "https://www.dekalbschoolsga.org/calendar/cat_ids~7/",
            "title": "board of education",
        },
    ]


def test_classification():
    assert meeting["classification"] == BOARD


def test_all_day():
    assert meeting["all_day"] is True
