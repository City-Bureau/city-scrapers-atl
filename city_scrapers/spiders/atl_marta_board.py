import re

import dateutil.parser
from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class AtlMartaBoardSpider(CityScrapersSpider):
    name = "atl_marta_board"
    agency = "MARTA Board of Directors"
    timezone = "America/Chicago"
    start_urls = ["https://www.itsmarta.com/meeting-schedule.aspx"]

    def parse(self, response):
        # not a lot here, just dates and titles
        for item in (
            response.xpath("//h2/following-sibling::ul")[0]
            .xpath("./li/descendant-or-self::*/text()")
            .getall()
        ):

            try:
                date, title = re.split(r"\s.\s", item)
            except ValueError:
                continue

            date = date.replace(", at ", " ").replace("Noon", "12pm")

            meeting = Meeting(
                title=title.strip(),
                description="",
                classification=NOT_CLASSIFIED,
                start=dateutil.parser.parse(date),
                end=None,
                all_day=False,
                time_notes="",
                links=[],
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
