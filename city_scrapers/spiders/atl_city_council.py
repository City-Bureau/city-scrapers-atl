from datetime import datetime
import re
from scrapy.http import Request

from city_scrapers_core.spiders import CityScrapersSpider

from ..mixins.iqm2 import IQM2Mixin


class AtlCityCouncilSpider(IQM2Mixin, CityScrapersSpider):
    name = "atl_city_council"
    agency = "Atlanta City Council"
    timezone = "America/New_York"

    iqm2_slug = "atlantacityga"
    board_name = "Atlanta City Council"

    def start_requests(self):
        current_year = datetime.now().year
        start_year = current_year - 3
        end_year = current_year + 1
        return [
            Request(
                f"https://{self.iqm2_slug}.iqm2.com/Citizens/calendar.aspx?View=List&From=1/1/{start_year}&To=12/31/{end_year}"
            )
        ]
    
    def _parse_links(self, item):
        links = []
        
        for link in item.xpath(".//a[contains(@href, 'FileOpen')]"):
            href = f"https://{self.iqm2_slug}.iqm2.com/Citizens/" + link.xpath("@href").get()
            title = link.css("::text").get()
            if href:
                links.append({"href": href, "title": title})
        
        for link in item.xpath(".//a[contains(@onclick, 'SplitView.aspx')]"):
            onclick = link.xpath("@onclick").get("")
            match = re.search(r'OpenWindow\("([^"]+)"', onclick)
            if match:
                href = f"https://{self.iqm2_slug}.iqm2.com" + match.group(1)
                title = link.css("::text").get()
                links.append({"href": href, "title": title})
        
        return links
    
    def _parse_source(self, response):
        """Parse or generate source."""
        source_url = "https://citycouncil.atlantaga.gov/other/events/public-meetings"
        return source_url


class AtlCityCouncilFinSpider(AtlCityCouncilSpider):
    name = "atl_city_council_fin"
    board_name = "Finance/Executive Committee"
    agency = "Atlanta City Council: {}".format(board_name)


class AtlCityCouncilUtilSpider(AtlCityCouncilSpider):
    name = "atl_city_council_utilities"
    board_name = "City Utilities Committee"
    agency = "Atlanta City Council: {}".format(board_name)


class AtlCityCouncilCOCSpider(AtlCityCouncilSpider):
    name = "atl_city_council_coc"
    board_name = "Committee on Council"
    agency = "Atlanta City Council: {}".format(board_name)


class AtlCityCouncilCDHSpider(AtlCityCouncilSpider):
    name = "atl_city_council_community"
    board_name = "Community Development/Human Services Committee"
    agency = "Atlanta City Council: {}".format(board_name)


class AtlCityCouncilSafetySpider(AtlCityCouncilSpider):
    name = "atl_city_council_safety"
    board_name = "Public Safety & Legal Administration Committee"
    agency = "Atlanta City Council: {}".format(board_name)


class AtlCityCouncilTransportationSpider(AtlCityCouncilSpider):
    name = "atl_city_council_transportation"
    board_name = "Transportation Committee"
    agency = "Atlanta City Council: {}".format(board_name)


class AtlCityCouncilZoningSpider(AtlCityCouncilSpider):
    name = "atl_city_council_zoning"
    board_name = "Zoning Committee"
    agency = "Atlanta City Council: {}".format(board_name)