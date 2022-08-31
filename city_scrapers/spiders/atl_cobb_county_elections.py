from city_scrapers_core.spiders import CityScrapersSpider

from ..mixins.cobb import CobbCountyDrupalMixin


class AtlCobbCountyElectionsSpider(CobbCountyDrupalMixin, CityScrapersSpider):
    name = "atl_cobb_county_elections"
    agency = "Cobb County Board of Elections"
    start_urls = ["https://www.cobbcounty.org/elections/events"]
