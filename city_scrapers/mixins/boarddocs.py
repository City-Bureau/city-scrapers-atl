import datetime
import random

from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from scrapy.http import Request


class BoardDocsMixin:
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
                time_notes="Sign-in is between 5:30 - 6:00 p.m",
                location={},
                links=[],
                source="https://go.boarddocs.com/ga/{self.boarddocs_slug}/Board.nsf/Public",  # noqa
            )
            self.augment_meeting(meeting, item)
            yield meeting

        def augment_meeting(self, meeting, item):
            pass
