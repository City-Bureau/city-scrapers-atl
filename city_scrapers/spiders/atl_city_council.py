from city_scrapers_core.spiders import CityScrapersSpider

from ..mixins.iqm2 import IQM2Mixin


class AtlCityCouncilSpider(IQM2Mixin, CityScrapersSpider):
    name = "atl_city_council"
    agency = "Atlanta City Council"
    timezone = "America/New_York"

    iqm2_slug = "atlantacityga"
    board_name = "Atlanta City Council"


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
