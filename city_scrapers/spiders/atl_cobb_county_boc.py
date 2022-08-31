from city_scrapers_core.spiders import CityScrapersSpider

from ..mixins.cobb import CobbCountyDrupalMixin


class AtlCobbCountyBocSpider(CobbCountyDrupalMixin, CityScrapersSpider):
    name = "atl_cobb_county_boc"
    agency = "Cobb County Board of Commissioners"
    start_urls = [
        "https://www.cobbcounty.org/events?field_section_target_id=All&field_event_category_target_id=195&field_event_date_recur_value_2=&field_event_date_recur_end_value="  # noqa
    ]
