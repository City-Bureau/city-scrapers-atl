import datetime
import random

from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from scrapy.http import Request


class BoardDocsMixin:
    """
    Usage:

    For a page like https://go.boarddocs.com/ga/fcss/Board.nsf/Public

    Set boarddocs_slug = "fcss" (part of URL after /ga/)
    Set boarddocs_committee_id = "AA6H9Z477333"
    (obtained via inspecting POST in browser while selecting meetings tab)

    Then override:
        augment_meeting(self, meeting, item)

    Which can add any extra data to 'meeting' (boarddocs only guarantee name and date).

    See Example: atl_gwinett_education.py
    """

    def start_requests(self):
        return [
            Request(
                f"https://go.boarddocs.com/ga/{self.boarddocs_slug}/Board.nsf/BD-GetMeetingsList?open&{random.random()}",  # noqa
                method="POST",
                body=f"current_committee_id={self.boarddocs_committee_id}",
            )
        ]

    def parse(self, response):
        for item in response.json():
            # blank items do occur
            if not item:
                continue
            meeting = Meeting(
                title=item["name"],
                description="",
                classification=NOT_CLASSIFIED,
                start=datetime.datetime.strptime(item["numberdate"], "%Y%m%d"),
                end=None,
                all_day=False,
                time_notes="",
                location={},
                links=[],
                source=f"https://go.boarddocs.com/ga/{self.boarddocs_slug}/Board.nsf/Public",  # noqa
            )
            self.augment_meeting(meeting, item)
            yield meeting

        def augment_meeting(self, meeting, item):
            pass

    # TODO:
    # second URL: https://go.boarddocs.com/ga/investatlanta/Board.nsf/BD-GetMeeting?open
    # body  id=CHBMGU58DB89 current_committee_id=AA6HBZ47C3A4
