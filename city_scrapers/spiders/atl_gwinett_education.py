from city_scrapers_core.spiders import CityScrapersSpider

from ..mixins.boarddocs import BoardDocsMixin


class AtlGwinettEducationSpider(BoardDocsMixin, CityScrapersSpider):
    name = "atl_gwinett_education"
    agency = "Gwinnett County Board of Education"
    timezone = "America/New_York"
    boarddocs_slug = "gcps"
    boarddocs_committee_id = "AA6HBM47B695"

    def augment_meeting(self, meeting, item):
        pass
