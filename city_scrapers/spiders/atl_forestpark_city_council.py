import re
from datetime import datetime

from city_scrapers_core.constants import BOARD, CITY_COUNCIL, COMMISSION, NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from scrapy import Request

# NOTE: This scraper requires scrapy-playwright for JavaScript rendering.
# The Forest Park website migrated to CivicClerk platform in 2025.
# If scrapy-playwright is not available, this scraper will not work.

BASE_URL = "https://forestparkga.portal.civicclerk.com"


class AtlForestparkCityCouncilSpider(CityScrapersSpider):
    name = "atl_forestpark_city_council"
    agency = "Forest Park City Council"
    timezone = "America/New_York"
    start_urls = [BASE_URL]
    location = {
        "name": "Forest Park City Hall",
        "address": "745 Forest Pkwy, Forest Park, GA 30297",
    }

    # Classification mapping based on meeting title keywords
    CLASSIFICATION_MAP = {
        "city council": CITY_COUNCIL,
        "council": CITY_COUNCIL,
        "commission": COMMISSION,
        "board": BOARD,
        "committee": COMMISSION,
        "authority": BOARD,
    }

    custom_settings = {
        # Enable Playwright for JavaScript rendering
        "DOWNLOAD_HANDLERS": {
            "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
            "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
        },
        "TWISTED_REACTOR": "twisted.internet.asyncioreactor.AsyncioSelectorReactor",
        "PLAYWRIGHT_BROWSER_TYPE": "chromium",
        "PLAYWRIGHT_LAUNCH_OPTIONS": {"headless": True},
    }

    def start_requests(self):
        """Generate requests with Playwright for JavaScript rendering."""
        yield Request(
            url=self.start_urls[0],
            meta={
                "playwright": True,
                "playwright_include_page": True,
                "playwright_page_methods": [
                    # Wait for the event list to load
                    {
                        "method": "wait_for_selector",
                        "args": ['[data-testid="eventList"]'],
                        "kwargs": {"timeout": 30000},
                    },
                    # Scroll to load more events
                    {"method": "evaluate", "args": ["window.scrollTo(0, 2000)"]},
                    # Wait a bit for dynamic content
                    {"method": "wait_for_timeout", "args": [2000]},
                ],
            },
            callback=self.parse,
        )

    def parse(self, response):
        """
        Parse meeting items from CivicClerk portal.

        The CivicClerk portal is a React application that requires JavaScript
        rendering. Meeting data is extracted from the rendered page content.
        Supports both CSS selector parsing (for structured HTML) and regex
        parsing (for text content).
        """
        content = response.css("body").get() or ""
        yielded = False

        # Method 1: Try CSS selectors for structured HTML (works with test fixtures)
        for article in response.css("article"):
            date_parts = article.css(".event-date span::text").getall()
            title = article.css(".event-title::text").get()
            location_text = article.css(".event-location::text").get()

            if not date_parts or not title:
                continue

            # Parse date parts: [day_name, "MON DD, YYYY", "HH:MM AM/PM TZ"]
            if len(date_parts) >= 3:
                date_str = date_parts[1]  # "NOV 21, 2025"
                time_str = date_parts[2]  # "12:00 PM EST"

                # Parse "MON DD, YYYY" format
                date_match = re.match(
                    r"([A-Z]{3})\s+(\d{1,2}),?\s*(\d{4})", date_str, re.IGNORECASE
                )
                if date_match:
                    month_abbr, day, year = date_match.groups()
                    start = self._parse_datetime(month_abbr, day, year, time_str)
                    if start:
                        meeting = Meeting(
                            title=self._clean_title(title),
                            description="",
                            classification=self._parse_classification(title),
                            start=start,
                            end=None,
                            all_day=False,
                            time_notes="",
                            location=self._parse_location_from_text(location_text),
                            links=self._parse_links(response, title),
                            source=response.url,
                        )
                        meeting["status"] = self._get_status(meeting, title)
                        meeting["id"] = self._get_id(meeting)
                        yield meeting
                        yielded = True

        # Method 2: Fall back to regex for text-based content (live site)
        if not yielded:
            meeting_pattern = re.compile(
                r"(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\s+"
                r"([A-Z]{3})\s+(\d{1,2}),?\s*(\d{4})\s+"
                r"(\d{1,2}:\d{2}\s*(?:AM|PM)\s*(?:EST|EDT)?)\s+"
                r"([^\n]+?)(?=\s*(?:Agenda|Monday|Tuesday|Wednesday|Thursday|"
                r"Friday|Saturday|Sunday|$))",
                re.IGNORECASE,
            )

            for match in meeting_pattern.finditer(content):
                day_name, month_abbr, day, year, time_str, title = match.groups()

                title = title.strip()
                if not title or len(title) < 3:
                    continue

                # Skip non-meeting entries
                if any(
                    skip in title.lower()
                    for skip in ["load more", "posted on", "search", "filter"]
                ):
                    continue

                start = self._parse_datetime(month_abbr, day, year, time_str)
                if not start:
                    continue

                meeting = Meeting(
                    title=self._clean_title(title),
                    description="",
                    classification=self._parse_classification(title),
                    start=start,
                    end=None,
                    all_day=False,
                    time_notes="",
                    location=self._parse_location(content, title),
                    links=self._parse_links(response, title),
                    source=response.url,
                )
                meeting["status"] = self._get_status(meeting, title)
                meeting["id"] = self._get_id(meeting)
                yield meeting

    def _parse_datetime(self, month_abbr, day, year, time_str):
        """Parse datetime from extracted components."""
        month_map = {
            "JAN": 1,
            "FEB": 2,
            "MAR": 3,
            "APR": 4,
            "MAY": 5,
            "JUN": 6,
            "JUL": 7,
            "AUG": 8,
            "SEP": 9,
            "OCT": 10,
            "NOV": 11,
            "DEC": 12,
        }

        try:
            month = month_map.get(month_abbr.upper())
            if not month:
                return None

            # Clean time string
            time_str = time_str.strip().upper().replace("EST", "").replace("EDT", "")
            time_str = re.sub(r"\s+", " ", time_str).strip()

            # Parse time
            try:
                time_obj = datetime.strptime(time_str, "%I:%M %p")
            except ValueError:
                try:
                    time_obj = datetime.strptime(time_str, "%I:%M%p")
                except ValueError:
                    return None

            return datetime(
                year=int(year),
                month=month,
                day=int(day),
                hour=time_obj.hour,
                minute=time_obj.minute,
            )
        except (ValueError, TypeError):
            return None

    def _clean_title(self, title):
        """Clean and normalize meeting title."""
        # Remove extra whitespace
        title = re.sub(r"\s+", " ", title).strip()
        # Remove location info that sometimes appears in title
        title = re.sub(r"\d+\s+Forest\s+Pkwy.*", "", title, flags=re.IGNORECASE)
        return title.strip()

    def _parse_classification(self, title):
        """Parse classification from meeting title."""
        title_lower = title.lower()
        for keyword, classification in self.CLASSIFICATION_MAP.items():
            if keyword in title_lower:
                return classification
        return NOT_CLASSIFIED

    def _parse_location_from_text(self, location_text):
        """Parse location from extracted location text."""
        if location_text:
            return {"name": "", "address": location_text.strip()}
        return self.location

    def _parse_location(self, content, title):
        """Parse location from content or use default."""
        # Check if location is mentioned near the title
        location_match = re.search(
            r"(\d+\s+Forest\s+Pkwy[^,]*,\s*Forest\s+Park,\s*GA\s*\d+)",
            content,
            re.IGNORECASE,
        )
        if location_match:
            return {"name": "", "address": location_match.group(1)}
        return self.location

    def _parse_links(self, response, title):
        """Generate links to the meeting portal."""
        return [{"href": response.url, "title": "Meeting Portal"}]
