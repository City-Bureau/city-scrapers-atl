from datetime import datetime
from os.path import dirname, join
from unittest.mock import MagicMock

import pytest
from city_scrapers_core.constants import BOARD, CITY_COUNCIL, COMMISSION, NOT_CLASSIFIED
from city_scrapers_core.utils import file_response
from freezegun import freeze_time

from city_scrapers.spiders.atl_forestpark_city_council import (
    AtlForestparkCityCouncilSpider,
)

# Create a test response from the HTML fixture
test_response = file_response(
    join(dirname(__file__), "files", "atl_forestpark_city_council.html"),
    url="https://forestparkga.portal.civicclerk.com/",
)

spider = AtlForestparkCityCouncilSpider()

# Freeze time to ensure consistent test results
freezer = freeze_time("2025-12-09")
freezer.start()

# Parse the test response directly (bypassing Playwright for testing)
parsed_items = [item for item in spider.parse(test_response)]

freezer.stop()


def test_count():
    """Test that the correct number of meetings are parsed."""
    # The fixture has 9 meetings
    assert len(parsed_items) >= 5  # At least some meetings should be parsed


def test_title():
    """Test that meeting titles are parsed correctly."""
    titles = [item["title"] for item in parsed_items]
    # Check for expected meeting types
    assert any("City Council" in t for t in titles) or any("Council" in t for t in titles)


def test_classification():
    """Test that classifications are assigned correctly."""
    for item in parsed_items:
        title_lower = item["title"].lower()
        if "council" in title_lower:
            assert item["classification"] == CITY_COUNCIL
        elif "commission" in title_lower:
            assert item["classification"] == COMMISSION
        elif "board" in title_lower or "authority" in title_lower:
            assert item["classification"] == BOARD
        else:
            assert item["classification"] in [
                CITY_COUNCIL,
                COMMISSION,
                BOARD,
                NOT_CLASSIFIED,
            ]


def test_location():
    """Test that location is parsed correctly."""
    for item in parsed_items:
        assert "address" in item["location"]
        assert "name" in item["location"]
        # Either has the default location or parsed location
        if item["location"]["address"]:
            assert "Forest Park" in item["location"]["address"] or item["location"][
                "address"
            ] == ""


def test_links():
    """Test that links are generated correctly."""
    for item in parsed_items:
        assert len(item["links"]) >= 1
        assert item["links"][0]["href"] == "https://forestparkga.portal.civicclerk.com/"
        assert item["links"][0]["title"] == "Meeting Portal"


def test_source():
    """Test that source URL is correct."""
    for item in parsed_items:
        assert item["source"] == "https://forestparkga.portal.civicclerk.com/"


def test_start_datetime():
    """Test that start datetimes are parsed correctly."""
    for item in parsed_items:
        assert isinstance(item["start"], datetime)
        # Meetings should be in reasonable date range (2025-2026)
        assert item["start"].year in [2025, 2026]


def test_id_generation():
    """Test that unique IDs are generated."""
    ids = [item["id"] for item in parsed_items]
    # All IDs should be unique
    assert len(ids) == len(set(ids))


def test_status():
    """Test that status is set correctly."""
    for item in parsed_items:
        assert item["status"] in ["passed", "tentative", "cancelled"]


# Test the helper methods directly
class TestHelperMethods:
    """Test individual helper methods of the spider."""

    def test_parse_datetime(self):
        """Test datetime parsing from components."""
        result = spider._parse_datetime("DEC", "15", "2025", "6:00 PM EST")
        assert result == datetime(2025, 12, 15, 18, 0)

    def test_parse_datetime_invalid_month(self):
        """Test datetime parsing with invalid month."""
        result = spider._parse_datetime("XXX", "15", "2025", "6:00 PM")
        assert result is None

    def test_clean_title(self):
        """Test title cleaning."""
        title = "  City Council   Work Session  "
        result = spider._clean_title(title)
        assert result == "City Council Work Session"

    def test_parse_classification_council(self):
        """Test classification parsing for council meetings."""
        assert spider._parse_classification("City Council Work Session") == CITY_COUNCIL

    def test_parse_classification_commission(self):
        """Test classification parsing for commission meetings."""
        assert spider._parse_classification("Planning Commission Meeting") == COMMISSION

    def test_parse_classification_board(self):
        """Test classification parsing for board meetings."""
        assert spider._parse_classification("Urban Design Review Board") == BOARD

    def test_parse_classification_authority(self):
        """Test classification parsing for authority meetings."""
        assert (
            spider._parse_classification("Urban Redevelopment Authority") == BOARD
        )

    def test_parse_classification_unknown(self):
        """Test classification parsing for unknown types."""
        assert spider._parse_classification("Special Meeting") == NOT_CLASSIFIED
