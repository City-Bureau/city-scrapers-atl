import re

import dateutil.parser
from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from scrapy.http import Request


class IQM2Mixin(CityScrapersSpider):
    board_name = None

    def start_requests(self):
        return [
            Request(
                f"https://{self.iqm2_slug}.iqm2.com/Citizens/Calendar.aspx?Frame=Yes&View=List&From=1/1/2021&To=12/31/2025"  # noqa
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
                description=self._parse_description(item),
                start=self._parse_start(item),
                classification=NOT_CLASSIFIED,
                end=None,
                all_day=False,
                time_notes="",
                location=self._parse_location(item),
                links=self._parse_links(item),
                source=self._parse_source(response),
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

    def _parse_location(self, item):
        """Parse or generate location."""
        return {
            "address": "",
            "name": "",
        }

    def _parse_links(self, item):
        links = []
        for link in item.xpath(".//a[contains(@href, 'FileOpen')]"):
            href = f"https://{self.iqm2_slug}.iqm2.com/" + link.xpath("@href").get()
            title = link.css("::text").get()
            if href:
                links.append({"href": href, "title": title})
        return links

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
