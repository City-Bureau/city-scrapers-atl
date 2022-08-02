from .atl_city_council import AtlCityCouncilSpider


class AtlCityCouncilFinSpider(AtlCityCouncilSpider):
    name = "atl_city_council_fin"
    board_name = "Finance/Executive Committee"
    agency = "Atlanta City Council: {}".format(board_name)
