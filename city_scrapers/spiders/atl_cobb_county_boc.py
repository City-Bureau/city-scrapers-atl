import datetime

import dateutil.parser
from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class AtlCobbCountyBocSpider(CityScrapersSpider):
    name = "atl_cobb_county_boc"
    agency = "Cobb County Board of Commissioners"
    timezone = "America/Chicago"
    start_urls = [
        "https://www.cobbcounty.org/events?field_section_target_id=All&field_event_category_target_id=195&field_event_date_recur_value_2=&field_event_date_recur_end_value="  # noqa
    ]

    def parse(self, response):
        for item in response.css("article.event-teaser"):
            meeting = Meeting(
                title=self._parse_title(item),
                description=self._parse_description(item),
                classification=self._parse_classification(item),
                start=self._parse_start(item),
                end=self._parse_end(item),
                all_day=self._parse_all_day(item),
                time_notes=self._parse_time_notes(item),
                location=self._parse_location(item),
                links=self._parse_links(item),
                source=self._parse_source(item),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        return item.xpath(".//h4/a/text()").get()

    def _parse_description(self, item):
        return ""

    def _parse_classification(self, item):
        return NOT_CLASSIFIED

    def _parse_start(self, item):
        month = item.css(".month-weekday::text").get()
        day = item.css(".day::text").get()
        year = datetime.datetime.today().year
        time = item.css(".time::text").get().split(" – ")[0]
        return dateutil.parser.parse(f"{month} {day} {year} {time}")

    def _parse_end(self, item):
        """Parse end datetime as a naive datetime object. Added by pipeline if None"""
        return None

    def _parse_time_notes(self, item):
        """Parse any additional notes on the timing of the meeting"""
        return ""

    def _parse_all_day(self, item):
        """Parse or generate all-day status. Defaults to False."""
        return False

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
