from datetime import datetime, timedelta

from city_scrapers_core.constants import ADVISORY_COMMITTEE, BOARD, COMMISSION
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class AtlBoeSpider(CityScrapersSpider):
    name = "atl_boe"
    agency = "Atlanta Board of Education"
    timezone = "America/New_York"
    start_urls = ["https://www.atlantapublicschools.us/apsboard"]
    custom_settings = {"COOKIES_ENABLED": True}
    weekdays = (
        "monday",
        "tuesday",
        "wednesday",
        "thursday",
        "friday",
        "saturday",
        "sunday",
    )

    def parse(self, response):
        for item in response.css(".ui-article"):
            if not item.css(".sw-calendar-block-date"):
                continue
            meeting = Meeting(
                title=self._parse_title(item),
                description="",
                classification=self._parse_classification(item),
                start=self._parse_start(item),
                end=self._parse_end(item),
                all_day=False,
                time_notes="",
                location=self._parse_location(item),
                links=self._parse_links(item),
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield response.follow(
                meeting["links"][0]["href"],
                callback=self._follow_meeting_link,
                meta={"meeting": meeting},
                dont_filter=True,
            )

    def _follow_meeting_link(self, response):
        """we only need to navigate this page in order to get
        the necessary cookies to interact with EventDetailWrapper.aspx,
        which is processed by _parse_meeting_details"""
        event_date_id = response.request.url.split("/")[-1]
        follow_link = (
            "https://www.atlantapublicschools.us/site/UserControls/Calendar"
            "/EventDetailWrapper.aspx?ModuleInstanceID=17299"
            f"&EventDateID={event_date_id}&UserRegID=0&IsEdit=false"
        )
        yield response.follow(
            follow_link,
            callback=self._parse_meeting_details,
            meta=response.meta,
            dont_filter=True,
        )

    def _parse_meeting_details(self, response):
        """parse the meeting details page to scrape
        a meeting notice if there is one"""
        meeting = response.meta["meeting"]
        meeting_notice = response.css(
            "#cal-ed-description-body > p > a::attr(href)"
        ).get()
        if meeting_notice:
            meeting_notice = response.urljoin(meeting_notice)
            meeting["links"].append({"href": meeting_notice, "title": "Meeting notice"})
        yield meeting

    def _parse_title(self, item):
        return item.css(".sw-calendar-block-title > a::text").get()

    def _parse_classification(self, item):
        if "committee" in self._parse_title(item).lower():
            return ADVISORY_COMMITTEE
        elif "commission" in self._parse_title(item).lower():
            return COMMISSION
        else:
            return BOARD

    def _parse_start(self, item):
        date = self._parse_date(item)
        time = self._parse_time(item, 0)
        return datetime(date.year, date.month, date.day, time.hour, time.minute)

    def _parse_end(self, item):
        date = self._parse_date(item)
        time = self._parse_time(item, 1)
        return datetime(date.year, date.month, date.day, time.hour, time.minute)

    def _parse_location(self, item):
        return {
            "address": "130 Trinity Avenue, Atlanta, GA 30303",
            "name": "Center for Learning and Leadership",
        }

    def _parse_links(self, item):
        """only parses meeting details link. the meeting notice,
        if it exists, is scraped from the meeting link"""
        href = item.css(".sw-calendar-block-title > a::attr(href)").get().strip()
        return [{"href": href, "title": "Meeting details"}]

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url

    def _parse_date(self, item):
        date_str = item.css(".sw-calendar-block-date::text").get()
        if date_str.lower() in self.weekdays:
            return self._get_next_weekday_date(date_str.lower())
        else:
            return datetime.strptime(date_str, "%B %d, %Y")

    def _parse_time(self, item, index):
        time_str = (
            item.css(".sw-calendar-block-time::text").get().split("-")[index].strip()
        )
        return datetime.strptime(time_str, "%I:%M %p")

    def _get_next_weekday_date(self, weekday):
        today = datetime.today()
        today_weekday = today.weekday()
        weekday_num = self.weekdays.index(weekday)
        return today + timedelta(days=(today_weekday - weekday_num) % 7 - 1)
