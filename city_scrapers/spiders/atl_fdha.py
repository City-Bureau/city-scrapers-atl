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
        """Parse location approximately in this order:
        item['venue']['address','city','state','zip']
        item['virtual_url']
        item['venue']['website']
        item['venue']['url']"""
        try:
            name = item["venue"]["venue"]
        except KeyError:
            name = "Virtual Event"

        if not self._event_is_virtual(item):
            try:
                state = (
                    self.state
                    if "state" not in item["venue"]
                    else item["venue"]["state"]
                )

                address = "{}, {}, {} {}".format(
                    item["venue"]["address"],
                    item["venue"]["city"],
                    state,
                    item["venue"]["zip"],
                )
            except KeyError:
                if "url" in item["venue"]:
                    address = item["venue"]["url"]
                else:
                    address = ""
        else:
            if item["virtual_url"]:
                address = item["virtual_url"]
            elif "website" in item["venue"]:
                address = item["venue"]["website"]
            else:
                address = item["venue"]["url"]

        return {
            "address": address,
            "name": name,
        }

    def _parse_links(self, item):
        links = []

        if item["website"]:
            links.append({"href": item["website"], "title": "Event Website"})

        organizer_links = [
            {"href": o["url"], "title": o["organizer"]} for o in item["organizer"]
        ]

        links = links + organizer_links
        return links

    def _event_is_virtual(self, item):
        return "virtual" in item["venue"]["venue"].lower()
