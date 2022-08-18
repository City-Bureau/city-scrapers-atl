import re

import dateutil.parser
from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class AtlCityCouncilSpider(CityScrapersSpider):
    name = "atl_city_council"
    agency = "Atlanta City Council"
    board_name = "Atlanta City Council"
    timezone = "America/New_York"
    start_urls = [
        "https://atlantacityga.iqm2.com/Citizens/Calendar.aspx?Frame=Yes"
        "&View=List&From=1/1/2021&To=12/31/2025"
    ]

    """
    Can scrape multiple boards w/ this, valid values for board name:
        Atlanta City Council
        City Utilities Committee
        Committee on Council
        Community Development/Human Services Committee
        Finance/Executive Committee
        Public Safety & Legal Administration Committee
        Transportation Committee
        Zoning Committee
    """

    def parse(self, response):
        for item in response.css(".MeetingRow"):
            desc = self._parse_description(item)
            board = re.findall(r"Board:\t(.*?)\r", desc)[0]
            # print(board)
            if board != self.board_name:
                continue
            meeting = Meeting(
                title=self._parse_title(item),
                description=self._parse_description(item),
                start=self._parse_start(item),
                classification=NOT_CLASSIFIED,
                end=None,
                all_day=False,
                time_notes="",
                location=self._parse_location(item),
                links=self._parse_links(item),
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_title(self, item):
        """Parse or generate meeting title."""
        return item.css(".RowDetails::text").get()

    def _parse_description(self, item):
        return item.css(".RowLink a").xpath("@title").get()

    def _parse_start(self, item):
        """Parse start datetime as a naive datetime object."""
        text = item.css(".RowLink a::text").get()
        return dateutil.parser.parse(text)

    def _parse_location(self, item):
        """Parse or generate location."""
        return {
            "address": "",
            "name": "",
        }

    def _parse_links(self, item):
        links = []
        for link in item.xpath(".//a[contains(@href, 'FileOpen')]"):
            href = "https://atlantacityga.iqm2.com/" + link.xpath("@href").get()
            title = link.css("::text").get()
            if href:
                links.append({"href": href, "title": title})
        return links

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url


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
