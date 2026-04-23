from datetime import datetime
from zoneinfo import ZoneInfo
import scrapy
from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class AtlWaterAndSewerAppealsBoardSpider(CityScrapersSpider):
    name = "atl_water_and_sewer_appeals_board"
    agency = "Atlanta City Council: Atlanta Water and Sewer Appeals Board"
    timezone = "America/New_York"
    start_urls = ["https://citycouncil.atlantaga.gov/other/events/public-meetings/-curm-1/-cury-2022"]
    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",
        "COOKIES_ENABLED": True,
        "DEFAULT_REQUEST_HEADERS": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Sec-Fetch-Dest": "document",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-User": "?1",
            "Upgrade-Insecure-Requests": "1",
        },
        "ROBOTSTXT_OBEY": False,
        "FEED_EXPORT_ENCODING": "utf-8",
    }

    def parse(self, response):
        for cell in response.css("td.calendar_day_with_items"):
            for item in cell.css("div.calendar_item"):
                title = item.css("a.calendar_eventlink::attr(title)").get("")
                if "Water and Sewer Appeals Board" not in title:
                    continue

                calendar_link = item.css("a.calendar_eventlink::attr(href)").get("")
                if calendar_link:
                    yield response.follow(
                        calendar_link,
                        callback=self._parse_detail,
                        meta={"title": title},
                    )

        next_url = response.css("a.next::attr(href)").get()
        if next_url and next_url.startswith("/"):
            yield response.follow(next_url, self.parse)

    def _parse_detail(self, response):
        title = response.meta["title"]
        start = self._parse_start(response)
        end = self._parse_end(response)

        links = [{"href": response.url, "title": "Agenda"}]

        meeting = Meeting(
            title=title,
            description="",
            classification=BOARD,
            start=start,
            end=end,
            all_day=False,
            time_notes="",
            location=self._parse_location(),
            links=links,
            source=response.url,
        )
        meeting["status"] = self._get_status(meeting)
        meeting["id"] = self._get_id(meeting)
        yield meeting

    def _parse_start(self, response):
        iso = response.css("time[itemprop='startDate']::attr(datetime)").get()
        if iso:
            return datetime.fromisoformat(iso).astimezone(ZoneInfo(self.timezone)).replace(tzinfo=None)
        return None

    def _parse_end(self, response):
        iso = response.css("time[itemprop='endDate']::attr(datetime)").get()
        if iso:
            return datetime.fromisoformat(iso).astimezone(ZoneInfo(self.timezone)).replace(tzinfo=None)
        return None

    def _parse_location(self):
        return {
            "address": "72 Marietta ST, Atlanta, GA 30303",
            "name": "Main Floor, Auditorium (Room 215)",
        }
