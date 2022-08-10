from datetime import datetime

from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class AtlCrbSpider(CityScrapersSpider):
    name = "atl_crb"
    agency = "Atlanta Citizen Review Board"
    timezone = "America/New_York"
    start_urls = ["https://acrbgov.org/"]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        links = self._parse_links(response)
        for entry in response.css("div.entry"):
            description = self._parse_description(entry)
            for item in entry.css("li"):

                meeting = Meeting(
                    title=self._parse_title(item),
                    description=description,
                    classification=NOT_CLASSIFIED,
                    start=self._parse_start(item),
                    end=None,
                    all_day=False,
                    time_notes="",
                    location=self._parse_location(item),
                    links=links,
                    source=self._parse_source(response),
                )

                meeting["status"] = self._get_status(meeting)
                meeting["id"] = self._get_id(meeting)

                yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        date_str = item.css("::text").getall()[0]
        return f"ACRB Meeting on {date_str}"

    def _parse_description(self, entry):
        """Parse or generate meeting description."""
        return entry.css("p > span::text").get().strip()

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        res = item.css("::text").getall()
        date_str = res[0]
        time_str = res[1].split()[:3]
        datetime_str = " ".join([date_str] + time_str)[:-1]
        fmt = "%B %d, %Y @ %I:%M %p"
        return datetime.strptime(datetime_str, fmt)

    def _parse_location(self, item):
        """Parse or generate location."""
        address = ",".join(item.css("::text").getall()[1].split(",")[1:]).strip()
        return {
            "address": address,
            "name": "Atlanta City Hall",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        res = item.css('a.eael-creative-button--default::attr("href")').get()
        title = item.css("span.cretive-button-text::text").get()
        return [{"href": res, "title": title}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
