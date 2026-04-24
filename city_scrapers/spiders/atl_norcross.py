from city_scrapers_core.spiders import CityScrapersSpider

from ..mixins.iqm2 import IQM2Mixin


class AtlNorcrossSpider(IQM2Mixin, CityScrapersSpider):
    name = "atl_norcross"
    agency = "Norcross City Council"
    timezone = "America/New_York"
    iqm2_slug = "norcrossga"
