from city_scrapers_core.constants import BOARD
from city_scrapers_core.spiders import EventsCalendarSpider


class AtlFdhaSpider(EventsCalendarSpider):
    name = "atl_fdha"
    agency = "Fulton-DeKalb Hospital Authority"
    timezone = "America/New_York"
    start_urls = ["https://thefdha.org/wp-json/tribe/events/v1/events"]
    categories = {
        BOARD: [
            "public-notices",
        ],
    }

    def _parse_location(self, item):
        return {}

    def _parse_links(self, item):
        return {}
