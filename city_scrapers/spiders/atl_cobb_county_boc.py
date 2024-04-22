from city_scrapers_core.spiders import CityScrapersSpider

from ..mixins.cobb import CobbCountyDrupalMixin


class AtlCobbCountyBocSpider(CobbCountyDrupalMixin, CityScrapersSpider):
    name = "atl_cobb_county_boc"
    agency = "Cobb County Board of Commissioners"
    # Filters for "type" of "public meeting" so that we ignore community events, etc.
    start_urls = ["https://www.cobbcounty.org/events?field_event_type_target_id=326"]
