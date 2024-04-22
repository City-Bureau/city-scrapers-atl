from datetime import datetime
from os.path import dirname, join

from city_scrapers_core.utils import file_response
from freezegun import freeze_time
from city_scrapers_core.constants import NOT_CLASSIFIED, PASSED
import json

from city_scrapers.spiders.atl_cobb_county_boc import AtlCobbCountyBocSpider

test_response = file_response(
    join(dirname(__file__), "files", "atl_cobb_county_boc.html"),
    url="https://www.cobbcounty.org/events?field_event_type_target_id=326",
)
spider = AtlCobbCountyBocSpider()

freezer = freeze_time("2024-04-24")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()

def test_title():
    assert parsed_items[0]["title"] == "Board of Commissioners Agenda Work Session"

def test_start():
    assert parsed_items[0]["start"] == datetime(2024, 4, 22, 9, 0)

def test_end():
    assert parsed_items[0]["end"] == None

def test_id():
    assert parsed_items[0]["id"] == "atl_cobb_county_boc/202404220900/x/board_of_commissioners_agenda_work_session"

def test_links():
    expected_links = [{'href': 'https://www.cobbcounty.org/events/23143', 'title': 'Event Details'}]
    assert parsed_items[0]["links"] == expected_links

def test_location():
    expected_location = {'address': '', 'name': 'TBD'}
    assert parsed_items[0]["location"] == expected_location

def test_source():
    assert parsed_items[0]["source"] == "https://www.cobbcounty.org/events?field_event_type_target_id=326"

def test_classification():
    assert parsed_items[0]["classification"] == NOT_CLASSIFIED

def test_description():
    assert parsed_items[0]["description"] == ""

def test_all_day():
    assert parsed_items[0]["all_day"] is False

def test_status():
    assert parsed_items[0]["status"] == PASSED

def test_time_notes():
    assert parsed_items[0]["time_notes"] == ""
