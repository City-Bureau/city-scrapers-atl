from datetime import datetime
from os.path import dirname, join

from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.forestpark_city_council import ForestparkCityCouncilSpider

test_response = file_response(
    join(dirname(__file__), "files", "forestpark_city_council.html"),
    url=(
        "https://www.forestparkga.gov/meetings?date_filter%5Bvalue%5D%5Bmonth%5D=1"
        "&date_filter%5Bvalue%5D%5Bday%5D=31&date_filter%5Bvalue%5D%5Byear%5D=2021"
        "&date_filter_1%5Bvalue%5D%5Bmonth%5D=12&date_filter_1%5Bvalue%5D%5Bday%5D=31"
        "&date_filter_1%5Bvalue%5D%5Byear%5D=2025&field_microsite_tid_1=All"
    ),
)
spider = ForestparkCityCouncilSpider()

freezer = freeze_time("2022-07-31")
freezer.start()

parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


"""
Uncomment below
"""


def test_title():
    assert parsed_items[0]["title"] == "City Council Regular Session"


# def test_description():
#     assert parsed_items[0]["description"] == "EXPECTED DESCRIPTION"


def test_start():
    assert parsed_items[0]["start"] == datetime(2023, 10, 9, 15, 6)


# def test_end():
#     assert parsed_items[0]["end"] == datetime(2019, 1, 1, 0, 0)


# def test_time_notes():
#     assert parsed_items[0]["time_notes"] == "EXPECTED TIME NOTES"


# def test_id():
#     assert parsed_items[0]["id"] == "EXPECTED ID"


# def test_status():
#     assert parsed_items[0]["status"] == "EXPECTED STATUS"


# def test_location():
#     assert parsed_items[0]["location"] == {
#         "name": "EXPECTED NAME",
#         "address": "EXPECTED ADDRESS"
#     }


# def test_source():
#     assert parsed_items[0]["source"] == "EXPECTED URL"


# def test_links():
#     assert parsed_items[0]["links"] == [{
#       "href": "EXPECTED HREF",
#       "title": "EXPECTED TITLE"
#     }]


# def test_classification():
#     assert parsed_items[0]["classification"] == NOT_CLASSIFIED


# @pytest.mark.parametrize("item", parsed_items)
# def test_all_day(item):
#     assert item["all_day"] is False
