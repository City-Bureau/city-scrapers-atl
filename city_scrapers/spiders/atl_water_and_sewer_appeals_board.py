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
    agency = "Atlanta Water and Sewer Appeals Board"
    timezone = "America/New_York"
    custom_settings = {
        "USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",  # noqa
        "COOKIES_ENABLED": True,
        "ROBOTSTXT_OBEY": False,
        "FEED_EXPORT_ENCODING": "utf-8",
        "DOWNLOAD_DELAY": 1,
        "AUTOTHROTTLE_ENABLED": True,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 4,
    }

    sharepoint_base_url = "https://cityofatlanta-my.sharepoint.com"
    folders_endpoint = "https://cityofatlanta-my.sharepoint.com/personal/appeals_atlantaga_gov/_api/web/GetListUsingPath(DecodedUrl=@a1)/RenderListDataAsStream?@a1=%27%2Fpersonal%2Fappeals%5Fatlantaga%5Fgov%2FDocuments%27&RootFolder=%2Fpersonal%2Fappeals%5Fatlantaga%5Fgov%2FDocuments%2FWater%20and%20Sewer%20Appeals%20Board&TryNewExperienceSingle=TRUE"  # noqa
    items_endpoint = "https://cityofatlanta-my.sharepoint.com/personal/appeals_atlantaga_gov/_api/web/GetListUsingPath(DecodedUrl=@a1)/RenderListDataAsStream?@a1=%27%2Fpersonal%2Fappeals%5Fatlantaga%5Fgov%2FDocuments%27&RootFolder={root_folder}"  # noqa
    sharepoint_url = "https://cityofatlanta-my.sharepoint.com/:f:/g/personal/appeals_atlantaga_gov/En0FGmWTfENHtqM7cf2A3W0BwBybjiODvcP1ngdKdYBiQg?e=jKmZdu"  # noqa
    sharepoint_headers = {
        "CollectSPPerfMetrics": "SPSQLQueryCount",
        "Referer": "https://cityofatlanta-my.sharepoint.com/personal/appeals_atlantaga_gov/_layouts/15/onedrive.aspx?id=%2Fpersonal%2Fappeals%5Fatlantaga%5Fgov%2FDocuments%2FWater%20and%20Sewer%20Appeals%20Board&ga=1",  # noqa
        "Origin": "https://cityofatlanta-my.sharepoint.com",
        "X-ServiceWorker-Strategy": "CacheFirst",
        "X-Service-Worker-Prefetch-And-Coalesce": "true",
        "X-SP-REQUESTRESOURCES": "listUrl=%2Fpersonal%2Fappeals%5Fatlantaga%5Fgov%2FDocuments",  # noqa
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36",  # noqa
        "Accept": "application/json;odata=verbose",
        "Content-Type": "application/json;odata=verbose",
    }
    time_notes = "See attachments for meeting time and location"

    # Folder names follow `YYYY-MM-DD-Hearing Schedules, Agendas, Summaries, Minutes`.
    # The calendar source on citycouncil.atlantaga.gov is geo-blocked at Akamai
    # for non-residential traffic, so meetings are derived from these folders alone.
    FOLDER_NAME_RE = re.compile(r"^(\d{4})-(\d{2})-(\d{2})-")
    MIN_YEAR = 2022
    MEETING_TITLE = "Water and Sewer Appeals Board"
    DEFAULT_START_HOUR = 9
    DEFAULT_START_MINUTE = 0
    SKIP_FILE_EXTENSIONS = (".pdf", ".doc", ".docx", ".xls", ".xlsx")

    def __init__(self, *args, **kwargs):
        # Per-instance copy so cookie/header mutation doesn't leak across runs
        self.sharepoint_headers = dict(type(self).sharepoint_headers)
        self._folder_links = {}
        self._folder_pending = {}
        super().__init__(*args, **kwargs)

    @property
    def tz(self):
        return ZoneInfo(self.timezone)

    def start_requests(self):
        yield scrapy.Request(
            url=self.sharepoint_url,
            callback=self._sharepoint_request,
        )

    def _sharepoint_request(self, response):
        cookie = response.headers.getlist("Set-Cookie")
        if cookie:
            self.sharepoint_headers["Cookie"] = cookie
        yield scrapy.Request(
            url=self.folders_endpoint,
            method="POST",
            headers=self.sharepoint_headers,
            callback=self._parse_folders,
            errback=self._sharepoint_errback,
            dont_filter=True,
        )

    def _parse_folders(self, response):
        try:
            data = response.json()
        except Exception as e:
            self.logger.error(
                "SharePoint folders response was not JSON: %s %s",
                e,
                response.text[:500],
            )
            return

        now = datetime.now(self.tz)
        end_year = now.year + 1

        for item in data.get("Row", []):
            file_ref = item.get("FileRef")
            folder_name = (item.get("FileLeafRef") or "").strip()
            if not file_ref or not folder_name:
                continue
            if folder_name.lower().endswith(self.SKIP_FILE_EXTENSIONS):
                continue

            match = self.FOLDER_NAME_RE.match(folder_name)
            if not match:
                continue
            year = int(match.group(1))
            if year < self.MIN_YEAR or year > end_year:
                continue

            self._folder_pending[folder_name] = (
                self._folder_pending.get(folder_name, 0) + 1
            )
            root_folder = urllib.parse.quote(file_ref, safe="")
            yield scrapy.Request(
                url=self.items_endpoint.format(root_folder=root_folder),
                method="POST",
                headers=self.sharepoint_headers,
                callback=self._parse_folder_items,
                errback=self._sharepoint_errback,
                meta={"folder_name": folder_name},
                dont_filter=True,
            )

        next_href = data.get("NextHref")
        if next_href:
            yield scrapy.Request(
                url=self._build_next_url(response, next_href),
                method="POST",
                headers=self.sharepoint_headers,
                callback=self._parse_folders,
                errback=self._sharepoint_errback,
                dont_filter=True,
            )

    def _parse_folder_items(self, response):
        folder_name = response.meta.get("folder_name", "")
        try:
            data = response.json()
        except Exception as e:
            self.logger.error(
                "SharePoint folder items not JSON for %s: %s %s",
                folder_name,
                e,
                response.text[:500],
            )
            yield from self._decrement_and_maybe_yield(folder_name)
            return

        links = self._parse_links(data.get("Row", []))
        if links:
            self._folder_links.setdefault(folder_name, []).extend(links)

        next_href = data.get("NextHref")
        if next_href:
            self._folder_pending[folder_name] = (
                self._folder_pending.get(folder_name, 0) + 1
            )
            yield scrapy.Request(
                url=self._build_next_url(response, next_href),
                method="POST",
                headers=self.sharepoint_headers,
                callback=self._parse_folder_items,
                errback=self._sharepoint_errback,
                meta={**response.meta},
                dont_filter=True,
            )

        yield from self._decrement_and_maybe_yield(folder_name)

    def _decrement_and_maybe_yield(self, folder_name):
        if not folder_name:
            return
        remaining = self._folder_pending.get(folder_name, 0) - 1
        self._folder_pending[folder_name] = remaining
        if remaining <= 0:
            meeting = self._build_meeting(
                folder_name, self._folder_links.get(folder_name, [])
            )
            if meeting is not None:
                yield meeting

    def _sharepoint_errback(self, failure):
        request = getattr(failure, "request", None)
        url = getattr(request, "url", "?")
        self.logger.warning(
            "SharePoint request failed (%s): %s",
            url,
            failure.getErrorMessage(),
        )
        meta = getattr(request, "meta", {}) or {}
        folder_name = meta.get("folder_name")
        if folder_name:
            yield from self._decrement_and_maybe_yield(folder_name)

    def _build_meeting(self, folder_name, links):
        match = self.FOLDER_NAME_RE.match(folder_name)
        if not match:
            self.logger.warning(
                "Folder name did not match date pattern: %s", folder_name
            )
            return None
        try:
            start = datetime(
                int(match.group(1)),
                int(match.group(2)),
                int(match.group(3)),
                self.DEFAULT_START_HOUR,
                self.DEFAULT_START_MINUTE,
            )
        except ValueError:
            self.logger.warning("Invalid date in folder name: %s", folder_name)
            return None

        if not links:
            links = [{"href": self.sharepoint_url, "title": "SharePoint Folder"}]

        meeting = Meeting(
            title=self.MEETING_TITLE,
            description="",
            classification=BOARD,
            start=start,
            end=None,
            all_day=False,
            time_notes=self.time_notes,
            location={"name": "", "address": ""},
            links=links,
            source=self.sharepoint_url,
        )
        meeting["status"] = self._get_status(meeting)
        meeting["id"] = self._get_id(meeting)
        return meeting

    def _build_next_url(self, response, next_href):
        if next_href.startswith("http"):
            return next_href
        if next_href.startswith("?"):
            base_url = response.url.split("?")[0]
            decoded_url = (
                "@a1=%27%2Fpersonal%2Fappeals%5Fatlantaga%5Fgov" "%2FDocuments%27"
            )
            return f"{base_url}?{decoded_url}&{next_href.lstrip('?')}"
        return response.urljoin(next_href)

    def _parse_links(self, rows):
        links = []
        for item in rows:
            raw_title = item.get("FileLeafRef", "")
            if not raw_title.lower().endswith(".pdf"):
                continue
            href = item.get("ServerRedirectedEmbedUrl") or item.get("FileRef", "")
            if not href:
                continue
            if href.startswith("/"):
                href = self.sharepoint_base_url + href
            title = self._clean_link_title(raw_title)
            links.append({"href": href, "title": title})
        return links

    def _clean_link_title(self, filename):
        name = re.sub(r"\.[^.]+$", "", filename)
        cleaned = re.sub(r"^.*?WSAB\s+", "", name)
        return cleaned if cleaned != name else name
