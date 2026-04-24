from datetime import datetime
import re

import dateutil.parser
from city_scrapers_core.constants import COMMITTEE, CITY_COUNCIL, NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from scrapy.http import Request


class IQM2Mixin(CityScrapersSpider):
    board_name = None
    source_url = None
    meeting_description = None

    def start_requests(self):
        current_year = datetime.now().year
        start_year = current_year - 3  # 3 years of history
        end_year = current_year + 1  # Include next year's scheduled meetings
        return [
            Request(
                f"https://{self.iqm2_slug}.iqm2.com/Citizens/Calendar.aspx?Frame=Yes&View=List&From=1/1/{start_year}&To=12/31/{end_year}"  # noqa
            )
        ]

    def parse(self, response):
        for item in response.css(".MeetingRow"):
            desc = self._parse_description(item)
            board = re.findall(r"Board:\t(.*?)\r", desc)[0]
            if self.board_name and board != self.board_name:
                continue
            meeting = Meeting(
                title=self._parse_title(item),
                description=self.meeting_description if self.meeting_description is not None else self._parse_description(item),  # noqa
                start=self._parse_start(item),
                classification=self._parse_classification(item),
                end=None,
                all_day=False,
                time_notes="",
                location=self._parse_location(item),
                links=self._parse_links(item),
                source=self.source_url or self._parse_source(response)
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return item.css(".RowDetails::text").get()

    def _parse_description(self, item):
        return item.css(".RowLink a").xpath("@title").get()

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        text = item.css(".RowLink a::text").get()
        return dateutil.parser.parse(text)

    def _parse_classification(self, _):
        """Parse or generate classification from allowed options."""
        if not self.board_name:
            return NOT_CLASSIFIED
        name = self.board_name.lower()
        if "city council" in name or "mayor and council" in name:
            return CITY_COUNCIL
        if "committee" in name:
            return COMMITTEE
        return NOT_CLASSIFIED

    def _parse_location(self, item):
        """Parse or generate location."""
        desc = self._parse_description(item) or ""
        match = re.search(r"Status:\t.*?\r\r\t(.*?)\r\t(.*?)$", desc, re.MULTILINE)
        if match:
            return {"name": match.group(1).strip(), "address": match.group(2).strip()}
        return {"name": "", "address": ""}

    def _parse_links(self, item):
        links = []

        for link in item.xpath(".//a[contains(@href, 'FileOpen')]"):
            href = f"https://{self.iqm2_slug}.iqm2.com/Citizens/" + link.xpath("@href").get()  # noqa
            title = link.css("::text").get()
            if href:
                links.append({"href": href, "title": title})

        for link in item.xpath(".//a[contains(@onclick, 'SplitView.aspx')]"):
            onclick = link.xpath("@onclick").get("")
            match = re.search(r'OpenWindow\("([^"]+)"', onclick)
            if match:
                href = f"https://{self.iqm2_slug}.iqm2.com" + match.group(1)
                title = link.css("::text").get()
                links.append({"href": href, "title": title})

        return links

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
