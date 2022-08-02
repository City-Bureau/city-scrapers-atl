import dateutil.parser
from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class AtlCityCouncilSpider(CityScrapersSpider):
    name = "atl_city_council"
    agency = "Atlanta City Council"
    timezone = "America/New_York"
    start_urls = [
        "https://atlantacityga.iqm2.com/Citizens/Calendar.aspx?Frame=Yes"
        "&View=List&From=1/1/2021&To=12/31/2025"
    ]

    def parse(self, response):
        for item in response.css(".MeetingRow"):
            # print(item.get())
            meeting = Meeting(
                title=self._parse_title(item),
                description="",
                classification=self._parse_classification(item),
                start=self._parse_start(item),
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

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return NOT_CLASSIFIED

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
        for link in item.css(".RowLink a"):
            href = "https://atlantacityga.iqm2.com/" + link.xpath("@href").get()
            title = link.css("::text").get()
            if href:
                links.append({"href": href, "title": title})
        return links

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
