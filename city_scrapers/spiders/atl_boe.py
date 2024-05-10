from datetime import datetime, timedelta

import scrapy
from city_scrapers_core.constants import BOARD, COMMISSION, COMMITTEE
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class AtlBoeSpider(CityScrapersSpider):
    name = "atl_boe"
    agency = "Atlanta Board of Education"
    timezone = "America/New_York"
    start_urls = [
        "https://www.atlantapublicschools.us/Generator/TokenGenerator.ashx/ProcessRequest"  # noqa
    ]
    calendar_base_url = "https://awsapieast1-prod23.schoolwires.com/REST/api/v4/CalendarEvents/GetEvents/17299"  # noqa
    default_location = {
        "name": "Atlanta Public Schools",
        "address": "130 Trinity Ave SW, Atlanta, GA 30303",
    }
    default_links = [
        {
            "title": "Atlanta BOE Facebook page",
            "href": "https://www.facebook.com/apsboard/",
        }
    ]

    def parse(self, response):
        """
        Get Bearer token from server's token generation endpoint
        and then make request to calendar API
        """
        data = response.json()
        token = data.get("Token")
        if not token:
            self.logger.error("No token found")
            return

        # Gen dates from 1 month ago to 3 months from today
        start_date = datetime.now() - timedelta(days=30)
        start_date_fmtd = start_date.strftime("%Y-%m-%d")
        end_date = datetime.now() + timedelta(days=90)
        end_date_fmtd = end_date.strftime("%Y-%m-%d")

        yield scrapy.Request(
            f"{self.calendar_base_url}?StartDate={start_date_fmtd}&EndDate={end_date_fmtd}&ModuleInstanceFilter=&CategoryFilter=&IsDBStreamAndShowAll=true",  # noqa
            callback=self.parse_events,
            headers={
                "Authorization": f"Bearer {token}",
                "Accept": "application/json",
                # The headers below are not strictly necessary but provided to
                # reduce the likelihood of being blocked by the server
                "Referer": "https://www.atlantapublicschools.us/",
                "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",  # noqa
            },
        )

    def parse_events(self, response):
        """
        Parse events from JSON response
        """
        try:
            events = response.json()
        except ValueError:
            self.logger.error("Failed to parse JSON from response")
            return

        for event in events:
            all_day = event.get("AllDay", False)
            meeting = Meeting(
                title=event["Title"].strip(),
                description="",
                classification=self._get_classification(event["Title"]),
                start=self._parse_datetime(event["Start"]),
                end=self._parse_datetime(event["End"]) if not all_day else None,
                all_day=event["AllDay"],
                time_notes=None,
                location=self.default_location,
                links=self.default_links,
                source=response.url,
            )
            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)
            yield meeting

    def _parse_datetime(self, datetime_str):
        """Convert ISO formatted date and time string to a datetime object."""
        return datetime.fromisoformat(datetime_str)

    def _get_classification(self, title):
        """Determine the classification based on the title or other fields."""
        clean_title = title.lower()
        if "board" in clean_title:
            return BOARD
        elif "committee" in clean_title:
            return COMMITTEE
        return COMMISSION
