import datetime

import dateutil.parser
from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting


class CobbCountyDrupalMixin:
    timezone = "America/New_York"
    base_url = "https://www.cobbcounty.org"

    def parse(self, response):
        for item in response.css("article.event-teaser"):
            title = self._parse_title(item)
            if "holiday" in title.lower():
                continue
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
                source=response.url,
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        return item.xpath(".//h4/text()").get()

    def _parse_start(self, item):
        month = item.css(".month-weekday::text").getall()[0]
        day = item.css(".day::text").get()
        year = datetime.datetime.today().year
        time = item.css(".event-time::text").get().split(" - ")[0]
        return dateutil.parser.parse(f"{month} {day} {year} {time}")

    def _parse_location(self, item):
        location_text = item.css(".event-location::text").get(default="").strip()
        location_text_clean = location_text.replace("Location(s):", "").strip()
        if not location_text_clean:
            return {
                "address": "",
                "name": "TBD",
            }
        return {
            "address": location_text_clean,
            "name": "",
        }

    def _parse_links(self, item):
        link_href = self.base_url + item.css("a::attr(href)").get()
        return [{"href": link_href, "title": "Event Details"}]

    def _parse_source(self, item):
        return self.base_url + item.css("a::attr(href)").get()
