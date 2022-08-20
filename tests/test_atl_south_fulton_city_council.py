from datetime import datetime
from os.path import dirname, join

from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.atl_south_fulton_city_council import (
    AtlSouthFultonCityCouncilSpider,
)

test_response = file_response(
    join(dirname(__file__), "files", "atl_south_fulton_city_council.html"),
    url="https://southfulton.novusagenda.com/agendapublic/meetingsresponsive.aspx",
)
spider = AtlSouthFultonCityCouncilSpider()

freezer = freeze_time("2022-08-20")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Council Regular Meeting"


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 8, 23, 16, 0)


def test_location():
    assert parsed_items[0]["location"] == {
        "name": "REGULAR COUNCIL MEETING",
        "address": "Welcome All Park Multipurpose Center  4255 Will Lee Road, South Fulton, GA ,30349",  # noqa
    }


def test_links():
    assert parsed_items[0]["links"] == [
        {
            "href": "https://southfulton.novusagenda.com/agendapublic/DisplayAgendaPDF.ashx?MeetingID=468",  # noqa
            "title": "Agenda (PDF)",
        }
    ]
