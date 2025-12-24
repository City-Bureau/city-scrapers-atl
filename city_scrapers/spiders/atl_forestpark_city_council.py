from datetime import datetime, timedelta

import scrapy
from city_scrapers_core.constants import BOARD, CITY_COUNCIL, COMMISSION, NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class ForestparkCityCouncilSpider(CityScrapersSpider):
    name = "atl_forestpark_city_council"
    agency = "Forest Park City Council"
    timezone = "America/New_York"

    API_BASE = "https://forestparkga.api.civicclerk.com/v1/Events"
    FILE_API_BASE = "https://forestparkga.api.civicclerk.com/v1/Meetings"
    PORTAL_BASE = "https://forestparkga.portal.civicclerk.com"

    location = {
        "name": "Forest Park City Hall",
        "address": "745 Forest Pkwy, Forest Park, GA 30297",
    }

    CLASSIFICATION_MAP = {
        "city council": CITY_COUNCIL,
        "council": CITY_COUNCIL,
        "commission": COMMISSION,
        "board": BOARD,
        "committee": COMMISSION,
        "authority": BOARD,
        "agency": BOARD,
    }

    def start_requests(self):
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%dT00:00:00Z")
        end_date = (datetime.now() + timedelta(days=90)).strftime("%Y-%m-%dT00:00:00Z")
        url = (
            f"{self.API_BASE}?"
            f"$filter=startDateTime ge {start_date} and startDateTime le {end_date}&"
            f"$orderby=startDateTime asc&$top=100"
        )
        yield scrapy.Request(url, callback=self.parse)

    def parse(self, response):
        data = response.json()

        for event in data.get("value", []):
            if event.get("isDeleted") or event.get("isPublished") != "Published":
                continue

            title = event.get("eventName", "").strip()
            if not title:
                continue

            start = self._parse_datetime(event.get("startDateTime"))
            if not start:
                continue

            meeting = Meeting(
                title=title,
                description=event.get("eventDescription", "").strip(),
                classification=self._parse_classification(
                    event.get("categoryName") or event.get("eventCategoryName") or title
                ),
                start=start,
                end=self._parse_datetime(event.get("meetingEndTime")),
                all_day=False,
                time_notes="",
                location=self._parse_location(event),
                links=self._parse_links(event),
                source=f"{self.PORTAL_BASE}/event/{event.get('id')}",
            )
            meeting["status"] = self._get_status(meeting, title)
            meeting["id"] = self._get_id(meeting)
            yield meeting

    def _parse_datetime(self, dt_str):
        if not dt_str:
            return None
        if dt_str.startswith("0001-") or dt_str.startswith("1900-"):
            return None
        try:
            dt_str = dt_str.replace("Z", "+00:00")
            dt = datetime.fromisoformat(dt_str)
            return dt.replace(tzinfo=None)
        except (ValueError, TypeError):
            return None

    def _parse_classification(self, category):
        if not category:
            return NOT_CLASSIFIED
        category_lower = category.lower()
        for keyword, classification in self.CLASSIFICATION_MAP.items():
            if keyword in category_lower:
                return classification
        return NOT_CLASSIFIED

    def _parse_location(self, event):
        event_location = event.get("eventLocation")
        if event_location and isinstance(event_location, dict):
            name = event_location.get("name", "").strip()
            address_parts = [
                event_location.get("address1", ""),
                event_location.get("city", ""),
                event_location.get("state", ""),
                event_location.get("zipCode") or event_location.get("zip", ""),
            ]
            address = ", ".join(p.strip() for p in address_parts if p and p.strip())
            if name or address:
                return {"name": name, "address": address}
        return self.location

    def _parse_links(self, event):
        links = []

        for file in event.get("publishedFiles", []):
            file_id = file.get("fileId")
            file_type = file.get("type", "Document")
            if file_id:
                href = (
                    f"{self.FILE_API_BASE}"
                    f"/GetMeetingFile(fileId={file_id},plainText=false)"
                )
                links.append({"href": href, "title": file_type})

        youtube_id = event.get("youtubeVideoId")
        if youtube_id:
            links.append(
                {
                    "href": f"https://www.youtube.com/watch?v={youtube_id}",
                    "title": "Video",
                }
            )

        external_url = event.get("externalMediaUrl")
        if external_url:
            links.append(
                {
                    "href": external_url,
                    "title": "Video",
                }
            )

        return links
