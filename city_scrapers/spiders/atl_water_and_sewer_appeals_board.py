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
        "DOWNLOAD_DELAY": 1,
        "AUTOTHROTTLE_ENABLED": True,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 4,
    }
    calendar_url = "https://citycouncil.atlantaga.gov/other/events/public-meetings/-curm-{month}/-cury-{year}"  # noqa
    tz = ZoneInfo(timezone)
    past_year_range = 4

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
    time_notes = "See attachments for accurate location details"

    def __init__(self, *args, **kwargs):
        self._sharepoint_links = {}
        self._pending_sharepoint_requests = 0
        self._calendar_started = False

        super().__init__(*args, **kwargs)

    def start_requests(self):
        yield scrapy.Request(
            url=self.sharepoint_url,
            callback=self._sharepoint_request,
        )

    def _sharepoint_request(self, response):
        try:
            cookie = response.headers.getlist("Set-Cookie")
            self.sharepoint_headers["Cookie"] = cookie
        except Exception as e:
            self.logger.error(
                "Failed to extract cookies from SharePoint response: %s", e
            )  # noqa
            return
        self._pending_sharepoint_requests += 1
        yield scrapy.Request(
            url=self.folders_endpoint,
            method="POST",
            headers=self.sharepoint_headers,
            callback=self._parse_folders,
            dont_filter=True,
        )

    def _parse_folders(self, response):
        try:
            data = response.json()
        except Exception as e:
            self.logger.error(
                "SharePoint folders response was not JSON: %s %s",
                e,
                response.text[:500],  # noqa
            )
            self._pending_sharepoint_requests -= 1
            yield from self._start_calendar()
            return

        now = datetime.now(self.tz)
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
                meta={"folder_name": item.get("FileLeafRef", "")},
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
                dont_filter=True,
            )

        self._pending_sharepoint_requests -= 1
        yield from self._start_calendar()

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
            self._pending_sharepoint_requests -= 1
            yield from self._start_calendar()
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
                meta={**response.meta},
                dont_filter=True,
            )

        self._pending_sharepoint_requests -= 1
        yield from self._start_calendar()

    def _start_calendar(self):
        if self._pending_sharepoint_requests > 0 or self._calendar_started:
            return

        self._calendar_started = True

        now = datetime.now(self.tz)
        year = now.year - self.past_year_range
        month = now.month

        while (year, month) <= (now.year, now.month):
            yield scrapy.Request(
                self.calendar_url.format(month=month, year=year),
                callback=self.parse,
                meta={"referrer_policy": "no-referrer"},
            )
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
                "@a1=%27%2Fpersonal%2Fappeals%5Fatlantaga%5Fgov" "%2FDocuments%27"
            )
            return f"{base_url}?{decoded_url}&{next_href.lstrip('?')}"
        if next_href.startswith("/"):
            return self.sharepoint_base_url + next_href
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
        cleaned = re.sub(r"^.*WSAB\s+", "", name)
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

        date_key = start.strftime("%Y-%m-%d")
        sharepoint_links = self._sharepoint_links.get(date_key, [])
        if sharepoint_links:
            links = sharepoint_links
        else:
            links = [{"href": response.url, "title": "Agenda"}]

        meeting = Meeting(
            title=title,
            description="",
            classification=BOARD,
            start=start,
            end=end,
            all_day=False,
            time_notes=self.time_notes,
            location={
                "name": "",
                "address": "",
            },
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
        if not iso:
            return None
        return datetime.fromisoformat(iso).replace(tzinfo=None)
