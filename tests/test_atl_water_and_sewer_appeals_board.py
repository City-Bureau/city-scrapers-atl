from datetime import datetime

import pytest
from city_scrapers_core.constants import BOARD
from freezegun import freeze_time

from city_scrapers.spiders.atl_water_and_sewer_appeals_board import (
    AtlWaterAndSewerAppealsBoardSpider,
)


@pytest.fixture
def spider():
    return AtlWaterAndSewerAppealsBoardSpider()


@freeze_time("2026-04-15")
def test_build_meeting_with_links(spider):
    folder_name = "2025-06-30-Hearing Schedules, Agendas, Summaries, Minutes"
    links = [
        {
            "href": "https://cityofatlanta-my.sharepoint.com/agenda.pdf",
            "title": "Agenda",
        }
    ]
    meeting = spider._build_meeting(folder_name, links)
    assert meeting["title"] == "Water and Sewer Appeals Board"
    assert meeting["description"] == ""
    assert meeting["classification"] == BOARD
    assert meeting["start"] == datetime(2025, 6, 30, 9, 0)
    assert meeting["end"] is None
    assert meeting["all_day"] is False
    assert meeting["status"] == "passed"
    assert meeting["location"] == {"name": "", "address": ""}
    assert meeting["links"] == links
    assert meeting["source"] == spider.sharepoint_url
    assert meeting["time_notes"] == "See attachments for meeting time and location"
    assert meeting["id"].startswith("atl_water_and_sewer_appeals_board/")


@freeze_time("2026-04-15")
def test_build_meeting_falls_back_to_sharepoint_link(spider):
    folder_name = "2026-05-15-Hearing Schedules, Agendas, Summaries, Minutes"
    meeting = spider._build_meeting(folder_name, [])
    assert meeting["status"] == "tentative"
    assert meeting["links"] == [
        {"href": spider.sharepoint_url, "title": "SharePoint Folder"}
    ]


def test_build_meeting_returns_none_for_invalid_name(spider):
    assert spider._build_meeting("README.pdf", []) is None
    assert spider._build_meeting("", []) is None
    assert spider._build_meeting("2025-13-99-Bad Date", []) is None


def test_parse_links_filters_pdfs_only(spider):
    rows = [
        {
            "FileLeafRef": "WSAB Agenda.pdf",
            "ServerRedirectedEmbedUrl": "https://example.com/agenda.pdf",
        },
        {
            "FileLeafRef": "thumbnail.jpg",
            "ServerRedirectedEmbedUrl": "https://example.com/thumb.jpg",
        },
        {
            "FileLeafRef": "Summary.PDF",
            "FileRef": "/personal/.../summary.pdf",
        },
    ]
    links = spider._parse_links(rows)
    assert len(links) == 2
    assert links[0] == {
        "href": "https://example.com/agenda.pdf",
        "title": "Agenda",
    }
    assert links[1]["href"].startswith("https://cityofatlanta-my.sharepoint.com/")


def test_clean_link_title_strips_extension_and_wsab_prefix(spider):
    assert spider._clean_link_title("WSAB Agenda.pdf") == "Agenda"
    assert spider._clean_link_title("Hearing Summary.pdf") == "Hearing Summary"


def test_clean_link_title_non_greedy_on_repeated_wsab(spider):
    # Non-greedy match — strips only the first WSAB prefix
    assert spider._clean_link_title("WSAB Agenda WSAB June.pdf") == "Agenda WSAB June"


def test_decrement_and_maybe_yield_yields_when_counter_hits_zero(spider):
    folder_name = "2025-06-30-Hearing Schedules, Agendas, Summaries, Minutes"
    spider._folder_pending[folder_name] = 1
    spider._folder_links[folder_name] = [
        {"href": "https://example.com/a.pdf", "title": "Agenda"}
    ]
    yielded = list(spider._decrement_and_maybe_yield(folder_name))
    assert len(yielded) == 1
    assert yielded[0]["title"] == "Water and Sewer Appeals Board"
    assert yielded[0]["start"].date() == datetime(2025, 6, 30).date()


def test_decrement_and_maybe_yield_waits_for_pagination(spider):
    folder_name = "2025-06-30-Hearing Schedules, Agendas, Summaries, Minutes"
    spider._folder_pending[folder_name] = 2
    yielded = list(spider._decrement_and_maybe_yield(folder_name))
    assert yielded == []
    assert spider._folder_pending[folder_name] == 1


def test_min_year_filter_constants(spider):
    assert spider.MIN_YEAR == 2022
    assert spider.FOLDER_NAME_RE.match(
        "2024-03-12-Hearing Schedules, Agendas, Summaries, Minutes"
    )
    assert not spider.FOLDER_NAME_RE.match("Reports Archive")
