from datetime import datetime
from zoneinfo import ZoneInfo
import urllib.parse

import scrapy
from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class AtlWaterAndSewerAppealsBoardSpider(CityScrapersSpider):
    name = "atl_water_and_sewer_appeals_board"
    agency = "Atlanta City Council: Atlanta Water and Sewer Appeals Board"
    timezone = "America/New_York"
    
    folders_endpoint = "https://cityofatlanta-my.sharepoint.com/personal/appeals_atlantaga_gov/_api/web/GetListUsingPath(DecodedUrl=@a1)/RenderListDataAsStream?@a1=%27%2Fpersonal%2Fappeals%5Fatlantaga%5Fgov%2FDocuments%27&RootFolder=%2Fpersonal%2Fappeals%5Fatlantaga%5Fgov%2FDocuments%2FWater%20and%20Sewer%20Appeals%20Board&TryNewExperienceSingle=TRUE"
    items_endpoint = "https://cityofatlanta-my.sharepoint.com/personal/appeals_atlantaga_gov/_api/web/GetListUsingPath(DecodedUrl=@a1)/RenderListDataAsStream?@a1=%27%2Fpersonal%2Fappeals%5Fatlantaga%5Fgov%2FDocuments%27&RootFolder={root_folder}"
    
    headers = {
        "CollectSPPerfMetrics": "SPSQLQueryCount",
        "Referer": "https://cityofatlanta-my.sharepoint.com/personal/appeals_atlantaga_gov/_layouts/15/onedrive.aspx?id=%2Fpersonal%2Fappeals%5Fatlantaga%5Fgov%2FDocuments%2FWater%20and%20Sewer%20Appeals%20Board&ga=1",
        "X-ServiceWorker-Strategy": "CacheFirst",
        "X-Service-Worker-Prefetch-And-Coalesce": "true",
        "X-SP-REQUESTRESOURCES": "listUrl=%2Fpersonal%2Fappeals%5Fatlantaga%5Fgov%2FDocuments",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
        "accept": "application/json;odata=verbose",
        "Content-Type": "application/json;odata=verbose",
        "Cookie": "ScaleCompatibilityDeviceId=0520bcc5-5a81-461c-957c-0877e33ffb65; FedAuth=77u/PD94bWwgdmVyc2lvbj0iMS4wIiBlbmNvZGluZz0idXRmLTgiPz48U1A+VjE1LDBoLmZ8bWVtYmVyc2hpcHx1cm4lM2FzcG8lM2F0ZW5hbnRhbm9uIzAzMWE1NTBhLWYxZjMtNGI2Mi05YzY0LTNlZjAyYzc3OThhNSwwIy5mfG1lbWJlcnNoaXB8dXJuJTNhc3BvJTNhdGVuYW50YW5vbiMwMzFhNTUwYS1mMWYzLTRiNjItOWM2NC0zZWYwMmM3Nzk4YTUsMTM0MjE3ODQ0MzgwMDAwMDAwLDAsMTM0MjE4NzA1MzkwMDE3NjM4LDAuMC4wLjAsMjU4LDAzMWE1NTBhLWYxZjMtNGI2Mi05YzY0LTNlZjAyYzc3OThhNSwsLDM3MjIwZWEyLWMwNDgtZDAwMC0wMDg3LTA3YTI2NWQ2NTlhMywzNzIyMGVhMi1jMDQ4LWQwMDAtMDA4Ny0wN2EyNjVkNjU5YTMsTll0UzV1M2JkMDZpSGdJN2UrM0YwdywwLDAsMCwsLCwyNjUwNDY3NzQzOTk5OTk5OTk5LDAsLCwsLCwsMCwsMTkyMzQ3LGZaVkYyQ2EzQjVhX2RDSnZzaTgwcEgyeUl1WSwsMCwsU2ZTZy82RzNReTlVSzdZeERlQ2tKc2lFSGlDSytTekFQdjNMZmFydnlzZHBPL29FcFN2bkJJenBhWFQzS3Q0K0JWT1Btb1pDQ3hlTldxbXphV1pDbXhiU0dHUlVQRFVRVDd3V1lPWkVDbjRLYjJ0bkpDSmRHTUF6R2NSbDdpVHovR3o2dFAwSXl6QWxQekxSd3FlOFd2L0FuclZ3SkRHa3hYaDFScHVYK2o4dkNXTmFOUW05NHJFdHJGYjhqeFRIb2VmR3JuUUJYbnd1THBRNGZvdmxCYUhIV3VzTUNhMFpnT2t6bVpaTVlNRlB2MnAvbkZzai9JOGdEbHZKRTIya3FrdENoNGU3cUYwa1h5U3pzcEw3NDEwb29ScE02RFZCL1V0ZU9NVTNGMFkvM3h5OFA3VCtvMzBSdjFkdlhURWhJZGthYjlYbTJrQXNxUVRwbXk2bHdnPT08L1NQPg==; SPHomeWeb:NGSP/experienceActive=false; FeatureOverrides_experiments=[]; msal.cache.encryption=%7B%22id%22%3A%22019dd0c2-440d-7aba-a9d6-3515ac3f88bc%22%2C%22key%22%3A%22XCsmY5NCEtzm4yW6nCtLTelXzccDMI1Q-9adbGEP3YU%22%7D; ai_session=S+zqEnWkrUe6t9kt9ffEdC|1777325556697|1777325556709"
    }

    def start_requests(self):
        yield scrapy.Request(
            url=self.folders_endpoint,
            method="POST",
            headers=self.headers,
            callback=self._parse_items,
        )

    def _parse_items(self, response):
        data = response.json().get("Row", [])
        for item in data:
            file_ref = item.get("FileRef")
            root_folder = urllib.parse.quote(file_ref, safe="")
            yield scrapy.Request(
                url=self.items_endpoint.format(root_folder=root_folder),
                method="POST",
                headers=self.headers,
                callback=self.parse,
            )
            break

    def parse(self, response):
        data = response.json().get("Row", [])
        links = self._parse_links(data)
        print(links)
        # meeting = Meeting(
        #     title=title,
        #     description="",
        #     classification=BOARD,
        #     start=start,
        #     end=end,
        #     all_day=False,
        #     time_notes="",
        #     location=self._parse_location(),
        #     links=links,
        #     source=response.url,
        # )
        # meeting["status"] = self._get_status(meeting)
        # meeting["id"] = self._get_id(meeting)
        # yield meeting
        yield None

    def _parse_links(self, data):
        links = []
        for item in data:
            title = item.get("FileLeafRef")
            href = item.get("ServerRedirectedEmbedUrl")
            if href:
                links.append({"href": href, "title": title})
        return links