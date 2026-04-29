from datetime import datetime
from zoneinfo import ZoneInfo

import scrapy
from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse as dateparser


class AtlClaytonCoBocSpider(CityScrapersSpider):
    name = "atl_clayton_co_boc"
    agency = "Clayton County Board of Commissioners"
    timezone = "America/New_York"
    source_url = "https://claytoncountyga.primegov.com/public/portal?fromiframe=true"
    archived_url = "https://claytoncountyga.primegov.com/api/v2/PublicPortal/ListArchivedMeetings?year={year}"  # noqa
    upcoming_url = (
        "https://claytoncountyga.primegov.com/api/v2/PublicPortal/ListUpcomingMeetings"
    )
    attachment_url = "https://claytoncountyga.primegov.com/Public/CompiledDocument?meetingTemplateId={template_id}&compileOutputType=1"  # noqa
    html_url = "https://claytoncountyga.primegov.com/Portal/Meeting?meetingTemplateId={template_id}"  # noqa

    """
    No address was found in the source website, so it is currently left blank.
    """
    meeting_address = {
        "address": "",
        "name": "",
    }

    time_notes = "For meeting's details, please refer to the source URL."

    custom_settings = {
        "ROBOTSTXT_OBEY": False,
    }

    def start_requests(self):
        yield scrapy.Request(
            url=self.upcoming_url, callback=self._parse_upcoming_meetings
        )

    def _parse_upcoming_meetings(self, response):
        meetings = response.json()
        for item in meetings:
            yield self.parse(item)

        current_year = datetime.now(ZoneInfo(self.timezone)).year
        for year in range(current_year - 3, current_year + 1):
            yield scrapy.Request(
                url=self.archived_url.format(year=year),
                callback=self._parse_archived_meetings,
            )

    def _parse_archived_meetings(self, response):
        meetings = response.json()
        for item in meetings:
            yield self.parse(item)

    def parse(self, item):
        title = item.get("title", "")
        meeting = Meeting(
            title=title,
            description="",
            classification=BOARD,
            start=self._parse_start(item),
            end=None,
            all_day=False,
            time_notes=self.time_notes,
            location=self.meeting_address,
            links=self._parse_links(item),
            source=self.source_url,
        )

        meeting["status"] = self._get_status(meeting)
        meeting["id"] = self._get_id(meeting)

        return meeting

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        date = item.get("date", "")
        time = item.get("time", "")
        parsed_start = None
        if date and time:
            dt_str = f"{date} {time}"
            parsed_start = dateparser(dt_str)
        elif date:
            parsed_start = dateparser(date)
        return parsed_start

    def _parse_links(self, item):
        links = []
        parsed_links = item.get("documentList", [])
        parsed_video_link = item.get("videoUrl", "")

        for link in parsed_links:
            if "HTML Agenda" in link.get("templateName", ""):
                href_link = self.html_url.format(template_id=link.get("templateId", ""))
            else:
                href_link = self.attachment_url.format(
                    template_id=link.get("templateId", "")
                )

            links.append(
                {
                    "title": link.get("templateName", ""),
                    "href": href_link,
                }
            )

        if parsed_video_link:
            links.append(
                {
                    "title": "Video",
                    "href": (
                        "https:" + parsed_video_link
                        if parsed_video_link.startswith("//")
                        else parsed_video_link
                    ),
                }
            )
        return links
