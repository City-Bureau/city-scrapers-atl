from city_scrapers_core.constants import COMMITTEE
from city_scrapers_core.spiders import EventsCalendarSpider


class AtlRegionalCommissionSpider(EventsCalendarSpider):
    name = "atl_regional_commission"
    agency = "Atlanta Regional Commission"
    timezone = "America/Chicago"
    start_urls = ["https://atlantaregional.org/wp-json/tribe/events/v1/events"]
    categories = {COMMITTEE: ["committees"]}

    # all Venue fields are set to the same generic "Georgia" location
    def _parse_location(self, item):
        return {"name": "", "address": ""}

    def _parse_links(self, item):
        return [{"href": item.get("url"), "title": "Event Website"}]
