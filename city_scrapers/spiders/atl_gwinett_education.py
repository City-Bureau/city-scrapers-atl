import re

import dateutil.parser
from city_scrapers_core.spiders import CityScrapersSpider

from ..mixins.boarddocs import BoardDocsMixin


class AtlGwinettEducationSpider(BoardDocsMixin, CityScrapersSpider):
    name = "atl_gwinett_education"
    agency = "Gwinnett County Board of Education"
    timezone = "America/New_York"
    boarddocs_slug = "gcps"
    boarddocs_committee_id = "AA6HBM47B695"

    def augment_meeting(self, meeting, item):
        # add time from title if present
        time = re.findall(r"\d{1,2}(?::\d{2})? [ap].m.", item["name"])
        if time:
            time = dateutil.parser.parse(time[0])
            meeting["start"] = meeting["start"].replace(
                hour=time.hour, minute=time.minute
            )
