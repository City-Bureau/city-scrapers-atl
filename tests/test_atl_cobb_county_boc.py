from datetime import datetime
from os.path import dirname, join

from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.atl_cobb_county_boc import AtlCobbCountyBocSpider

test_response = file_response(
    join(dirname(__file__), "files", "atl_cobb_county_boc.html"),
    url="https://www.cobbcounty.org/events?field_section_target_id=All&field_event_category_target_id=195&field_event_date_recur_value_2=&field_event_date_recur_end_value=",  # noqa
)
spider = AtlCobbCountyBocSpider()

freezer = freeze_time("2022-08-20")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_title():
    assert parsed_items[0]["title"] == "Board of Commissioners Agenda Work Session"


def test_start():
    assert parsed_items[0]["start"] == datetime(2022, 8, 22, 9, 0)


def test_source():
    assert (
        parsed_items[0]["source"]
        == "https://www.cobbcounty.org/board/events/board-commissioners-agenda-work-session-43"  # noqa
    )
