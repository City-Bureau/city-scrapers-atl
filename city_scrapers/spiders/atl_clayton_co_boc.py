from city_scrapers_core.spiders import CityScrapersSpider

from ..mixins.iqm2 import IQM2Mixin


class AtlClaytonCoBocSpider(IQM2Mixin, CityScrapersSpider):
    name = "atl_clayton_co_boc"
    agency = "Clayton County Board of Commissioners"
    timezone = "America/New_York"
    iqm2_slug = "claytoncountyga"
