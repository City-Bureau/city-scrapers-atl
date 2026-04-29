import re
import urllib.parse
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
    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",  # noqa
        "COOKIES_ENABLED": True,
        "DEFAULT_REQUEST_HEADERS": {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",  # noqa
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

    folders_endpoint = "https://cityofatlanta-my.sharepoint.com/personal/appeals_atlantaga_gov/_api/web/GetListUsingPath(DecodedUrl=@a1)/RenderListDataAsStream?@a1=%27%2Fpersonal%2Fappeals%5Fatlantaga%5Fgov%2FDocuments%27&RootFolder=%2Fpersonal%2Fappeals%5Fatlantaga%5Fgov%2FDocuments%2FWater%20and%20Sewer%20Appeals%20Board&TryNewExperienceSingle=TRUE"  # noqa
    items_endpoint = "https://cityofatlanta-my.sharepoint.com/personal/appeals_atlantaga_gov/_api/web/GetListUsingPath(DecodedUrl=@a1)/RenderListDataAsStream?@a1=%27%2Fpersonal%2Fappeals%5Fatlantaga%5Fgov%2FDocuments%27&RootFolder={root_folder}"  # noqa

    sharepoint_headers = {
        "CollectSPPerfMetrics": "SPSQLQueryCount",
        "Referer": "https://cityofatlanta-my.sharepoint.com/personal/appeals_atlantaga_gov/_layouts/15/onedrive.aspx?id=%2Fpersonal%2Fappeals%5Fatlantaga%5Fgov%2FDocuments%2FWater%20and%20Sewer%20Appeals%20Board&ga=1",  # noqa
        "Origin": "https://cityofatlanta-my.sharepoint.com",
        "X-ServiceWorker-Strategy": "CacheFirst",
        "X-Service-Worker-Prefetch-And-Coalesce": "true",
        "X-SP-REQUESTRESOURCES": "listUrl=%2Fpersonal%2Fappeals%5Fatlantaga%5Fgov%2FDocuments",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",  # noqa
        "Accept": "application/json;odata=verbose",
        "Content-Type": "application/json;odata=verbose",
        "Cookie": "FeatureOverrides_experiments=[]; msal.cache.encryption=%7B%22id%22%3A%22019d90ba-7921-79f8-a9fb-c08fe6114c74%22%2C%22key%22%3A%22OrlBukcfy2yB9YnoU6S9NuMUXyI5X76kTfV8HblHce8%22%7D; SPHomeWeb:NGSP/experienceActive=false; ScaleCompatibilityDeviceId=8ae86ad4-72c9-481a-bc52-af8b082b1771; FedAuth=77u/PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0idXRmLTgiPz48U1A+VjE1LDBoLmZ8bWVtYmVyc2hpcHx1cm4lM2FzcG8lM2F0ZW5hbnRhbm9uIzAzMWE1NTBhLWYxZjMtNGI2Mi05YzY0LTNlZjAyYzc3OThhNSwwIy5mfG1lbWJlcnNoaXB8dXJuJTNhc3BvJTNhdGVuYW50YW5vbiMwMzFhNTUwYS1mMWYzLTRiNjItOWM2NC0zZWYwMmM3Nzk4YTUsMTM0MjE5NTAyNzkwMDAwMDAwLDAsMTM0MjIwMzYzNzk2NzE4NTY2LDAuMC4wLjAsMjU4LDAzMWE1NTBhLWYxZjMtNGI2Mi05YzY0LTNlZjAyYzc3OThhNSwsLDVmYzAwZWEyLTAwYWItZDAwMC0wMDg3LTAzNTVlNGZmZjQwZSw1ZmMwMGVhMi0wMGFiLWQwMDAtMDA4Ny0wMzU1ZTRmZmY0MGUsaWVjRHhSODBzRXljbWdQNzlKVXhDUSwwLDAsMCwsLCwyNjUwNDY3NzQzOTk5OTk5OTk5LDAsLCwsLCwsMCwsMTkyMzQ3LGZaVkYyQ2EzQjVhX2RDSnZzaTgwcEgyeUl1WSwsMCwsWG9ScmpJWFRkZ1ZEb08xMGZpMmh2K0VacXh4dEI1T3d2OHYvRjJlWnFHMDR3MmxGMjNxNmdzSm03cHNKWTZQZGNwSlBHbHhTV2I2cWk1WnpNTVhvSG56VWtYeVQ2aWU5RmVDdHBZajEyTDFUTk9CM0RJMGdScEtKV2F5dUhkMWhTbXF5VERRclplUmlyZU1UR0lVelVrS3ZuRXhIOXZTOXZwOVZlbWdSaGNzNHFQRGxrdktHOWJ6bURmZzdUMHllQjd6enl3MGZwWnB4YWFTSU0xc3RnNnROVWkyYmcvZTFRMDNzWWRRcDFIY01VdmVzNklINXFtZXJReGhEbmUzakxzWTJnQjExb3VUODhlMjNmQ1MyVTIzQnRNZ1FLcFEvYXY0NDYwN01zbkFtMmNCRWtLZVdzOUE3aVR4Nms1YUd6dGVZTE1jSjc0ekxiaEQ5RHRwYTl3PT08L1NQPg==",  # noqa
    }

    def __init__(self, *args, **kwargs):
        self._sharepoint_links = {}
        self._pending_sharepoint_requests = 0
        self._calendar_started = False

        super().__init__(*args, **kwargs)

    def start_requests(self):
        self._pending_sharepoint_requests += 1
        yield scrapy.Request(
            url=self.folders_endpoint,
            method="POST",
            headers=self.sharepoint_headers,
            callback=self._parse_folders,
            errback=self._sharepoint_errback,
            dont_filter=True,
            meta={"dont_merge_cookies": True},
        )

    def _parse_folders(self, response):
        try:
            data = response.json()
        except Exception:
            self.logger.error(
                "SharePoint folders response was not JSON: %s", response.text[:500]
            )
            self._pending_sharepoint_requests -= 1
            yield from self._maybe_start_calendar()
            return

        now = datetime.now(ZoneInfo(self.timezone))
        end_year = now.year + 1

        for item in data.get("Row", []):
            file_ref = item.get("FileRef")
            if not file_ref:
                continue

            folder_name = item.get("FileLeafRef", "")
            year_match = re.match(r"^(\d{4})", folder_name)
            if year_match:
                item_year = int(year_match.group(1))
                if item_year < 2022 or item_year > end_year:
                    continue

            root_folder = urllib.parse.quote(file_ref, safe="")
            self._pending_sharepoint_requests += 1

            yield scrapy.Request(
                url=self.items_endpoint.format(root_folder=root_folder),
                method="POST",
                headers=self.sharepoint_headers,
                callback=self._parse_folder_items,
                errback=self._sharepoint_errback,
                meta={"folder_name": item.get("FileLeafRef", ""), "dont_merge_cookies": True},
                dont_filter=True,
            )

        next_href = data.get("NextHref")
        if next_href:
            self._pending_sharepoint_requests += 1
            yield scrapy.Request(
                url=self._build_next_url(response, next_href),
                method="POST",
                headers=self.sharepoint_headers,
                callback=self._parse_folders,
                errback=self._sharepoint_errback,
                dont_filter=True,
                meta={"dont_merge_cookies": True},
            )

        self._pending_sharepoint_requests -= 1
        yield from self._maybe_start_calendar()

    def _parse_folder_items(self, response):
        folder_name = response.meta.get("folder_name", "")

        try:
            data = response.json()
        except Exception:
            self.logger.error(
                "SharePoint folder items not JSON for %s: %s",
                folder_name,
                response.text[:500],
            )
            self._pending_sharepoint_requests -= 1
            yield from self._maybe_start_calendar()
            return

        links = self._parse_links(data.get("Row", []))
        date_key = self._parse_folder_date(folder_name)
        if date_key and links:
            self._sharepoint_links.setdefault(date_key, []).extend(links)

        next_href = data.get("NextHref")
        if next_href:
            self._pending_sharepoint_requests += 1
            yield scrapy.Request(
                url=self._build_next_url(response, next_href),
                method="POST",
                headers=self.sharepoint_headers,
                callback=self._parse_folder_items,
                errback=self._sharepoint_errback,
                meta={**response.meta, "dont_merge_cookies": True},
                dont_filter=True,
            )

        self._pending_sharepoint_requests -= 1
        yield from self._maybe_start_calendar()

    def _sharepoint_errback(self, failure):
        self.logger.error("SharePoint request failed: %s", failure)
        self._pending_sharepoint_requests -= 1
        yield from self._maybe_start_calendar()

    def _maybe_start_calendar(self):
        if self._pending_sharepoint_requests > 0 or self._calendar_started:
            return

        self._calendar_started = True

        now = datetime.now(ZoneInfo(self.timezone))
        year = now.year - 4
        month = now.month

        while (year, month) <= (now.year, now.month):
            url = (
                "https://citycouncil.atlantaga.gov/other/events/public-meetings"
                f"/-curm-{month}/-cury-{year}"
            )
            yield scrapy.Request(url, callback=self.parse)
            month += 1
            if month > 12:
                month = 1
                year += 1

    def parse(self, response):
        for cell in response.css("td.calendar_day_with_items"):
            for item in cell.css("div.calendar_item"):
                title = item.css("a.calendar_eventlink::attr(title)").get("")
                if "water and sewer appeals board" not in title.lower():
                    continue

                calendar_link = item.css("a.calendar_eventlink::attr(href)").get("")
                if calendar_link:
                    yield response.follow(
                        calendar_link,
                        callback=self._parse_detail,
                        meta={"title": title},
                    )

    def _build_next_url(self, response, next_href):
        if next_href.startswith("http"):
            return next_href
        if next_href.startswith("?"):
            base_url = response.url.split("?")[0]
            decoded_url = (
                "@a1=%27%2Fpersonal%2Fappeals%5Fatlantaga%5Fgov"
                "%2FDocuments%27"
            )
            return f"{base_url}?{decoded_url}&{next_href.lstrip('?')}"
        if next_href.startswith("/"):
            return "https://cityofatlanta-my.sharepoint.com" + next_href
        return response.urljoin(next_href)

    def _parse_links(self, rows):
        links = []
        for item in rows:
            raw_title = item.get("FileLeafRef", "")
            href = item.get("ServerRedirectedEmbedUrl") or item.get("FileRef", "")
            if not href:
                continue
            if href.startswith("/"):
                href = "https://cityofatlanta-my.sharepoint.com" + href
            title = self._clean_link_title(raw_title)
            links.append({"href": href, "title": title})
        return links

    def _clean_link_title(self, filename):
        name = re.sub(r"\.[^.]+$", "", filename)
        cleaned = re.sub(r"^.*-WSAB\s+", "", name)
        return cleaned if cleaned != name else name

    def _parse_folder_date(self, folder_name):
        match = re.match(r"^(\d{4}-\d{2}-\d{2})", folder_name.strip())
        if match:
            return match.group(1)
        return folder_name

    def _parse_detail(self, response):
        title = response.meta["title"]
        start = self._parse_start(response)
        if not start:
            return
        end = self._parse_end(response)

        links = [{"href": response.url, "title": "Agenda"}]
        date_key = start.strftime("%Y-%m-%d")
        sharepoint_links = self._sharepoint_links.get(date_key, [])
        links.extend(sharepoint_links)

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
        return self._parse_datetime(response, "startDate")

    def _parse_end(self, response):
        return self._parse_datetime(response, "endDate")

    def _parse_datetime(self, response, itemprop):
        iso = response.css(f"time[itemprop='{itemprop}']::attr(datetime)").get()
        if iso:
            return (
                datetime.fromisoformat(iso)
                .astimezone(ZoneInfo(self.timezone))
                .replace(tzinfo=None)
            )
        return None

    def _parse_location(self):
        return {
            "address": "72 Marietta ST, Atlanta, GA 30303",
            "name": "Main Floor, Auditorium (Room 215)",
        }
