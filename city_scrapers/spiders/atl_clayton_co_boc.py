from datetime import datetime

from city_scrapers_core.spiders import CityScrapersSpider
from scrapy.http import Request

from ..mixins.iqm2 import IQM2Mixin


class AtlClaytonCoBocSpider(IQM2Mixin, CityScrapersSpider):
    name = "atl_clayton_co_boc"
    agency = "Clayton County Board of Commissioners"
    timezone = "America/New_York"
    iqm2_slug = "claytoncountyga"

    def start_requests(self):
        current_year = datetime.now().year
        start_year = current_year - 3  # 3 years of history
        end_year = current_year + 1  # Include next year's scheduled meetings
        return [
            Request(
                f"https://{self.iqm2_slug}.iqm2.com/Citizens/Calendar.aspx?Frame=Yes&View=List&From=1/1/{start_year}&To=12/31/{end_year}"  # noqa
            )
        ]
    

    def _parse_links(self, item):
        links = []
        for link in item.xpath(".//a[contains(@href, 'FileOpen')]"):
            href = f"https://{self.iqm2_slug}.iqm2.com/" + link.xpath("@href").get()
            title = link.css("::text").get()
            if href:
                links.append({"href": href, "title": title})
        return links
    

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
