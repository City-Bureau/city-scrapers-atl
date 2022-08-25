from city_scrapers_core.constants import ADVISORY_COMMITTEE, BOARD, FORUM
from city_scrapers_core.spiders import EventsCalendarSpider


class AtlBeltlineSpider(EventsCalendarSpider):
    name = "atl_beltline"
    state = "GA"
    agency = "Atlanta BeltLine Inc."
    timezone = "America/New_York"
    start_urls = ["https://beltline.org/wp-json/tribe/events/v1/events"]
    categories = {
        BOARD: [
            "abi-board-meetings",
            "abi-execeutive-committee-meetings",
            "leadership",
        ],
        FORUM: [
            "community-meetings",
            "economic-development",
            "housing",
            "bahab-meetings",
        ],
        ADVISORY_COMMITTEE: ["design-review-committee"],
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
        return item["is_virtual"] or "virtual" in item["venue"]["venue"].lower()
