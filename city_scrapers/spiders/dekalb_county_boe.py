from datetime import datetime

from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from scrapy.linkextractors.lxmlhtml import LxmlLinkExtractor


class DekalbCountyBoeSpider(CityScrapersSpider):
    name = "dekalb_county_boe"
    agency = "DeKalb County Board of Education"
    timezone = "America/New_York"
    start_urls = ["https://www.dekalbschoolsga.org/board-of-education/board-meetings/"]
    link_extractor = LxmlLinkExtractor(restrict_css=".ai1ec-event-details")

    def parse(self, response):
        for item in response.css("a.ai1ec-read-more::attr(href)"):
            print(item.get())
            yield response.follow(
                item.get(),
                callback=self._parse_meeting_page,
            )

    def _parse_meeting_page(self, response):
        start, end, all_day = self._parse_time(response.css(".dt-duration"))
        meeting = Meeting(
            title=self._parse_title(response),
            description=self._parse_description(response),
            classification=BOARD,
            start=start,
            end=end,
            all_day=all_day,
            time_notes="",
            location=self._parse_location(response),
            links=self._parse_links(response),
            source=self._parse_source(response),
        )

        meeting["status"] = self._get_status(meeting)
        meeting["id"] = self._get_id(meeting)

        yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return item.css(".entry-title::text").get()

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return "\n".join(item.css(".post-content > p").getall())

    def _parse_time(self, dt_duration):
        start_str = dt_duration.css("::text").get().strip()
        all_day = True if dt_duration.css(".ai1ec-allday-badge") else False
        if all_day:
            start = datetime.strptime(start_str, "%B %d, %Y")
            end = None
        else:
            start_str, end_time = start_str.split("–")
            start = datetime.strptime(start_str, "%B %d, %Y @ %I:%M %p")
            end = datetime.strptime(end_time, "%I:%M %p")
            end = start.replace(hour=end.hour, minute=end.minnute)
        return start, end, all_day

    def _parse_location(self, item):
        address = [
            a.strip() for a in item.css(".p-location::text").getall() if a.strip()
        ]
        return {
            "address": ", ".join(address[1:]),
            "name": address[0],
        }

    def _parse_links(self, item):
        links = [
            {
                "href": "https://www.dekalbschoolsga.org/communications/dstv",
                "title": "DSTV (Comcast channel 24)",
            }
        ]
        for link in self.link_extractor.extract_links(item):
            links.append({"href": link.url, "title": link.text.strip()})
        return links

    def _parse_source(self, response):
        return response.url
