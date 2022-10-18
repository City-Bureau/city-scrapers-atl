import dateutil.parser
from city_scrapers_core.constants import CITY_COUNCIL, NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider

BASE_URL = "https://www.forestparkga.gov"


class ForestParkSpider(CityScrapersSpider):
    """to add meetings from other boards, add the slug (the first part of the URL
    under "View Details") to the categories dict"""

    name = "atl_forestpark"
    agency = "Forest Park"
    timezone = "America/New_York"
    start_urls = ["https://www.forestparkga.gov/meetings"]
    categories = {
        CITY_COUNCIL: ["citycouncil"],
        NOT_CLASSIFIED: ["bc-ura"],
    }

    def parse(self, response):
        for item in response.css(".views-table tbody tr"):
            classification = self._parse_classification(item)
            print(classification)
            if classification:
                meeting = Meeting(
                    title=self._parse_title(item),
                    description=self._parse_description(item),
                    classification=classification,
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
        """Parse or generate meeting title."""
        return item.css(".views-field-title::text").get().strip()

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        for td in item.css("td"):
            slug = item.css(".views-field-view-node a::attr(href)").get().split("/")[1]
            print(slug)
            for CLASSIFICATION in self.categories:
                if slug in self.categories[CLASSIFICATION]:
                    return CLASSIFICATION
            return None

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
            "address": "745 Forest Parkway, Forest Park, GA 30297",
            "name": "Forest Park City Council",
        }

    def _parse_link(self, field):
        href = field.css("a::attr(href)").get()
        if href:
            return {
                "href": BASE_URL + href,
                "title": field.css("::attr(data-th)").get(),
            }

    def _parse_links(self, item):
        return [
            link
            for link in (self._parse_link(field) for field in item.css(".views-field"))
            if link
        ]

    def _parse_source(self, item):
        return BASE_URL + item.css(".views-field-view-node a::attr(href)").get()
