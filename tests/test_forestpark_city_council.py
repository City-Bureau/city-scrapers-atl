import json
from datetime import datetime
from pathlib import Path

import pytest
from city_scrapers_core.constants import BOARD, CITY_COUNCIL, COMMISSION, NOT_CLASSIFIED
from freezegun import freeze_time

from city_scrapers.spiders.atl_forestpark_city_council import (
    ForestparkCityCouncilSpider,
)

FIXTURE_PATH = Path(__file__).parent / "files" / "forestpark_city_council.json"


class MockResponse:
    def __init__(self, data):
        self._data = data
        self.url = "https://forestparkga.api.civicclerk.com/v1/Events"

    def json(self):
        return self._data


@pytest.fixture
def spider():
    return ForestparkCityCouncilSpider()


@pytest.fixture
def parsed_items(spider):
    with freeze_time("2024-12-03"):
        with open(FIXTURE_PATH) as f:
            data = json.load(f)
        response = MockResponse(data)
        return list(spider.parse(response))


def test_count(parsed_items):
    assert len(parsed_items) == 4


def test_title(parsed_items):
    assert parsed_items[0]["title"] == "City Council Work Session"
    assert parsed_items[1]["title"] == "Planning Commission Meeting"
    assert parsed_items[2]["title"] == "Development Authority Meeting-- CANCELED"
    assert parsed_items[3]["title"] == "Urban Redevelopment Agency Meeting"


def test_description(parsed_items):
    assert parsed_items[0]["description"] == "Regular work session"
    assert parsed_items[1]["description"] == ""
    assert parsed_items[3]["description"] == "Monthly agency meeting"


def test_start(parsed_items):
    assert parsed_items[0]["start"] == datetime(2024, 12, 2, 18, 0)
    assert parsed_items[1]["start"] == datetime(2024, 12, 5, 18, 0)
    assert parsed_items[2]["start"] == datetime(2024, 12, 10, 17, 30)


def test_end(parsed_items):
    assert parsed_items[0]["end"] == datetime(2024, 12, 2, 20, 0)
    assert parsed_items[1]["end"] is None
    assert parsed_items[3]["end"] == datetime(2024, 12, 15, 19, 30)


def test_classification(parsed_items):
    assert parsed_items[0]["classification"] == CITY_COUNCIL
    assert parsed_items[1]["classification"] == COMMISSION
    assert parsed_items[2]["classification"] == BOARD
    assert parsed_items[3]["classification"] == BOARD


def test_status(parsed_items):
    assert parsed_items[0]["status"] == "passed"
    assert parsed_items[1]["status"] == "tentative"
    assert parsed_items[2]["status"] == "cancelled"


def test_location_with_data(parsed_items):
    assert parsed_items[0]["location"]["name"] == "City Hall"
    assert "745 Forest Pkwy" in parsed_items[0]["location"]["address"]
    assert "Forest Park" in parsed_items[0]["location"]["address"]
    assert "GA" in parsed_items[0]["location"]["address"]
    assert "30297" in parsed_items[0]["location"]["address"]


def test_location_default(parsed_items, spider):
    assert parsed_items[1]["location"] == spider.location
    assert parsed_items[2]["location"] == spider.location


def test_links_with_files_and_video(parsed_items):
    links = parsed_items[0]["links"]
    assert len(links) == 3

    agenda_links = [link for link in links if link["title"] == "Agenda"]
    assert len(agenda_links) == 1
    assert "GetMeetingFile(fileId=100" in agenda_links[0]["href"]

    packet_links = [link for link in links if link["title"] == "Agenda Packet"]
    assert len(packet_links) == 1
    assert "GetMeetingFile(fileId=101" in packet_links[0]["href"]

    video_links = [link for link in links if link["title"] == "Video"]
    assert len(video_links) == 1
    assert "youtube.com" in video_links[0]["href"]
    assert "abc123" in video_links[0]["href"]


def test_links_with_agenda_only(parsed_items):
    links = parsed_items[3]["links"]
    assert len(links) == 1
    assert links[0]["title"] == "Agenda"
    assert "GetMeetingFile(fileId=200" in links[0]["href"]


def test_links_empty(parsed_items):
    links = parsed_items[1]["links"]
    assert len(links) == 0


def test_source(parsed_items):
    assert "event/569" in parsed_items[0]["source"]
    assert "forestparkga.portal.civicclerk.com" in parsed_items[0]["source"]


def test_id_uniqueness(parsed_items):
    ids = [item["id"] for item in parsed_items]
    assert len(ids) == len(set(ids))


def test_all_day(parsed_items):
    for item in parsed_items:
        assert item["all_day"] is False


def test_time_notes(parsed_items):
    for item in parsed_items:
        assert item["time_notes"] == ""


def test_deleted_meetings_excluded(spider):
    with freeze_time("2024-12-03"):
        with open(FIXTURE_PATH) as f:
            data = json.load(f)
        response = MockResponse(data)
        items = list(spider.parse(response))
        titles = [item["title"] for item in items]
        assert "Deleted Meeting" not in titles


def test_unpublished_meetings_excluded(spider):
    unpublished_response = {
        "value": [
            {
                "id": 999,
                "eventName": "Draft Meeting",
                "eventDescription": "",
                "startDateTime": "2024-12-25T18:00:00Z",
                "meetingEndTime": "1900-01-01T00:00:00Z",
                "isPublished": "Draft",
                "isDeleted": False,
                "categoryName": "City Council",
                "hasAgenda": False,
                "agendaId": None,
                "youtubeVideoId": "",
                "publishedFiles": [],
                "eventLocation": None,
            }
        ]
    }
    response = MockResponse(unpublished_response)
    items = list(spider.parse(response))
    assert len(items) == 0


class TestHelperMethods:
    def test_parse_datetime_valid(self, spider):
        result = spider._parse_datetime("2024-12-02T18:00:00Z")
        assert result == datetime(2024, 12, 2, 18, 0)

    def test_parse_datetime_with_offset(self, spider):
        result = spider._parse_datetime("2024-12-02T18:00:00+00:00")
        assert result == datetime(2024, 12, 2, 18, 0)

    def test_parse_datetime_invalid(self, spider):
        assert spider._parse_datetime(None) is None
        assert spider._parse_datetime("") is None
        assert spider._parse_datetime("invalid") is None

    def test_parse_datetime_placeholder_0001(self, spider):
        assert spider._parse_datetime("0001-01-01T00:00:00Z") is None

    def test_parse_datetime_placeholder_1900(self, spider):
        assert spider._parse_datetime("1900-01-01T00:00:00Z") is None

    def test_parse_classification_city_council(self, spider):
        assert spider._parse_classification("City Council") == CITY_COUNCIL
        assert spider._parse_classification("city council meeting") == CITY_COUNCIL

    def test_parse_classification_council(self, spider):
        assert spider._parse_classification("Council") == CITY_COUNCIL

    def test_parse_classification_commission(self, spider):
        assert spider._parse_classification("Planning Commission") == COMMISSION
        assert spider._parse_classification("commission") == COMMISSION

    def test_parse_classification_board(self, spider):
        assert spider._parse_classification("Review Board") == BOARD
        assert spider._parse_classification("board meeting") == BOARD

    def test_parse_classification_committee(self, spider):
        assert spider._parse_classification("Beautification Committee") == COMMISSION

    def test_parse_classification_authority(self, spider):
        assert spider._parse_classification("Development Authority") == BOARD

    def test_parse_classification_agency(self, spider):
        assert spider._parse_classification("Urban Redevelopment Agency") == BOARD

    def test_parse_classification_unknown(self, spider):
        assert spider._parse_classification("Special Meeting") == NOT_CLASSIFIED

    def test_parse_classification_none(self, spider):
        assert spider._parse_classification(None) == NOT_CLASSIFIED

    def test_parse_classification_empty(self, spider):
        assert spider._parse_classification("") == NOT_CLASSIFIED

    def test_parse_location_with_zipcode(self, spider):
        event = {
            "eventLocation": {
                "name": "City Hall",
                "address1": "123 Main St",
                "city": "Forest Park",
                "state": "GA",
                "zipCode": "30297",
            }
        }
        result = spider._parse_location(event)
        assert result["name"] == "City Hall"
        assert "123 Main St" in result["address"]
        assert "Forest Park" in result["address"]
        assert "30297" in result["address"]

    def test_parse_location_with_zip_fallback(self, spider):
        event = {
            "eventLocation": {
                "name": "City Hall",
                "address1": "123 Main St",
                "city": "Forest Park",
                "state": "GA",
                "zip": "30297",
            }
        }
        result = spider._parse_location(event)
        assert result["name"] == "City Hall"
        assert "30297" in result["address"]

    def test_parse_location_without_name(self, spider):
        event = {
            "eventLocation": {
                "name": "",
                "address1": "123 Main St",
                "city": "Forest Park",
                "state": "GA",
                "zipCode": "30297",
            }
        }
        result = spider._parse_location(event)
        assert result["name"] == ""
        assert "123 Main St" in result["address"]

    def test_parse_location_none(self, spider):
        event = {"eventLocation": None}
        result = spider._parse_location(event)
        assert result == spider.location

    def test_parse_location_empty_dict(self, spider):
        event = {"eventLocation": {}}
        result = spider._parse_location(event)
        assert result == spider.location

    def test_parse_links_with_files(self, spider):
        event = {
            "publishedFiles": [
                {"fileId": 123, "type": "Agenda"},
                {"fileId": 456, "type": "Minutes"},
            ],
            "youtubeVideoId": "",
            "externalMediaUrl": "",
        }
        links = spider._parse_links(event)
        assert len(links) == 2
        assert links[0]["title"] == "Agenda"
        assert "fileId=123" in links[0]["href"]
        assert links[1]["title"] == "Minutes"
        assert "fileId=456" in links[1]["href"]

    def test_parse_links_with_video(self, spider):
        event = {
            "publishedFiles": [],
            "youtubeVideoId": "xyz789",
            "externalMediaUrl": "",
        }
        links = spider._parse_links(event)
        assert len(links) == 1
        assert links[0]["title"] == "Video"
        assert "youtube.com" in links[0]["href"]
        assert "xyz789" in links[0]["href"]

    def test_parse_links_with_external_video(self, spider):
        event = {
            "publishedFiles": [],
            "youtubeVideoId": "",
            "externalMediaUrl": "https://example.com/video.mp4",
        }
        links = spider._parse_links(event)
        assert len(links) == 1
        assert links[0]["title"] == "Video"
        assert links[0]["href"] == "https://example.com/video.mp4"

    def test_parse_links_empty(self, spider):
        event = {
            "publishedFiles": [],
            "youtubeVideoId": "",
            "externalMediaUrl": "",
        }
        links = spider._parse_links(event)
        assert len(links) == 0

    def test_parse_links_missing_file_id(self, spider):
        event = {
            "publishedFiles": [
                {"type": "Agenda"},
            ],
            "youtubeVideoId": "",
            "externalMediaUrl": "",
        }
        links = spider._parse_links(event)
        assert len(links) == 0
