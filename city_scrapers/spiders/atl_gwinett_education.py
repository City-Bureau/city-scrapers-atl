from city_scrapers_core.spiders import CityScrapersSpider

from ..mixins.boarddocs import BoardDocsMixin


class AtlGwinettEducationSpider(BoardDocsMixin, CityScrapersSpider):
    name = "atl_gwinett_education"
    agency = "Gwinnett County Board of Education"
    timezone = "America/New_York"
    boarddocs_slug = "fcss"
    boarddocs_committee_id = "AA6H9Z477333"

    def augment_meeting(self, meeting, item):
        # set time on all meetings
        meeting["start"] = meeting["start"].replace(hour=18)
        meeting["time_notes"] = "Sign-in is between 5:30 - 6:00 p.m"
