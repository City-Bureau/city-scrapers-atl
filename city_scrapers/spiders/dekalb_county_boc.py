from datetime import datetime

from city_scrapers_core.constants import CITY_COUNCIL
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.tz import gettz


class DekalbCountyBocSpider(CityScrapersSpider):
    name = "dekalb_county_boc"
    agency = "DeKalb County Board of Commissioners"
    timezone = "America/New_York"
    start_urls = ["https://www.dekalbcountyga.gov/meeting-calendar"]

    def parse(self, response):
        for item in response.css(
            "table.full > tbody > tr > td > .inner > .item > .view-item "
            "> .calendar.monthview > div:not([class^='cutoff'])"
        ):
            title = self._parse_title(item)
            if not self._is_boc_meeting(title):
                continue

            meeting = Meeting(
                title=title,
                description="",
                classification=CITY_COUNCIL,
                start=self._parse_datetime(item, 0),
                end=self._parse_datetime(item, 1),
                all_day=False,
                time_notes="",
                location=self._parse_location(item),
                links=[],
                source=self._parse_source(response, item),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield response.follow(
                meeting["source"],
                callback=self._parse_meeting,
                meta={"meeting": meeting},
            )

    def _parse_meeting(self, response):
        meeting = response.meta["meeting"]
        meeting["links"] = self._parse_links(response.css(".desc > div > p > a"))

        yield meeting

    def _parse_links(self, item):
        public_participation = [
            {
                "href": "https://www.dekalbcountyga.gov/"
                "board-commissioners/public-participation",
                "title": "Public Participation",
            }
        ]
        scraped_links = [
            {"href": link.css("::attr(href)").get(), "title": link.css("::text").get()}
            for link in item
        ]
        return scraped_links + public_participation

    def _parse_title(self, item):
        return item.css("a::attr(title)").get()

    def _parse_datetime(self, item, num):
        datetime_str = (
            item.css("time::attr(datetime)").getall()[num].replace("Z", "+00:00")
        )
        return (
            datetime.fromisoformat(datetime_str)
            .astimezone(gettz(self.timezone))
            .replace(tzinfo=None)
        )

    def _parse_location(self, item):
        """
        these meetings are virtual until further notice
        the physical address:
        return {
            "address": "1300 Commerce Drive, Decatur, GA 30030",
            "name": "MPR, 5th Floor, Manuel J. Maloof Administration Building",
        }
        """
        return {
            "address": "",
            "name": "",
        }

    def _parse_source(self, response, item):
        return response.urljoin(item.css("a::attr(href)").get())

    def _is_boc_meeting(self, title):
        committees = (
            "Board of Commissioners",
            "Committee of the Whole",
            "County Operations",
            "Employee Relations and Public Safety",
            "Finance Audit and Budget",
            "Planning Economic Development and Community Services",
            "Public Works and Infrastructure",
        )
        title_clean = (
            title.strip()
            .lower()
            .replace(",", "")
            .replace("&amp;", "and")
            .replace("&", "and")
        )
        for committee in committees:
            if committee.lower() in title_clean:
                return True
        return False
