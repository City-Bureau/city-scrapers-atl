import datetime

import dateutil.parser
from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting


class CobbCountyDrupalMixin:
    timezone = "America/New_York"

    def parse(self, response):
        for item in response.css("article.event-teaser"):
            meeting = Meeting(
                title=self._parse_title(item),
                description="",
                classification=NOT_CLASSIFIED,
                start=self._parse_start(item),
                end=None,
                all_day=False,
                time_notes="",
                location=self._parse_location(item),
                links=self._parse_links(item),
                source=self._parse_source(item),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        return item.xpath(".//h4/a/text()").get()

    def _parse_start(self, item):
        month = item.css(".month-weekday::text").get()
        day = item.css(".day::text").get()
        year = datetime.datetime.today().year
        time = item.css(".time::text").get().split(" – ")[0]
        return dateutil.parser.parse(f"{month} {day} {year} {time}")

    def _parse_location(self, item):
        """Parse or generate location."""
        return {
            "address": "",
            "name": "",
        }

    def _parse_links(self, item):
        """Parse or generate links."""
        return [{"href": "", "title": ""}]

    def _parse_source(self, item):
        """Parse or generate source."""
        return "https://www.cobbcounty.org" + item.xpath(".//h4/a/@href").get()
