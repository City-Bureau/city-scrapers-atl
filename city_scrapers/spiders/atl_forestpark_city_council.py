import dateutil.parser
from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider

BASE_URL = "https://www.forestparkga.gov"


class ForestparkCityCouncilSpider(CityScrapersSpider):
    name = "atl_forestpark_city_council"
    agency = "Forest Park City Council"
    timezone = "America/New_York"
    start_urls = [
        (
            "https://www.forestparkga.gov/meetings?date_filter%5Bvalue%5D%5Bmonth%5D=1"
            "&date_filter%5Bvalue%5D%5Bday%5D=1&date_filter%5Bvalue%5D%5Byear%5D=2021"
            "&date_filter_1%5Bvalue%5D%5Bmonth%5D=12"
            "&date_filter_1%5Bvalue%5D%5Bday%5D=31"
            "&date_filter_1%5Bvalue%5D%5Byear%5D=2025&field_microsite_tid_1=All"
        )
    ]

    def parse(self, response):
        """
        `parse` should always `yield` Meeting items.

        Change the `_parse_title`, `_parse_start`, etc methods to fit your scraping
        needs.
        """
        for item in response.css(".views-table tbody tr"):
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
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return item.css(".views-field-title::text").get().strip()

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return NOT_CLASSIFIED

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        date = item.css(".views-field-field-calendar-date span").xpath("@content").get()
        return dateutil.parser.parse(date).replace(tzinfo=None)

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
        return [
            {
                "href": BASE_URL
                + item.css(".views-field-view-node a").xpath("@href").get(),
                "title": "View Details",
            }
        ]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
