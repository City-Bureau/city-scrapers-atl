from city_scrapers_core.spiders import CityScrapersSpider

from ..mixins.boarddocs import BoardDocsMixin


class AtlInvestAtlantaSpider(BoardDocsMixin, CityScrapersSpider):
    name = "atl_invest_atlanta"
    agency = "Invest Atlanta"
    timezone = "America/New_York"
    boarddocs_slug = "investatlanta"
    boarddocs_committee_id = "AA6HBZ47C3A4"

    def augment_meeting(self, meeting, item):
        pass
