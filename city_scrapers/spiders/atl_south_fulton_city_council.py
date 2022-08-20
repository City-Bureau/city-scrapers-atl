import dateutil.parser
from city_scrapers_core.constants import NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class AtlSouthFultonCityCouncilSpider(CityScrapersSpider):
    name = "atl_south_fulton_city_council"
    agency = "South Fulton City Council"
    timezone = "America/Chicago"
    start_urls = [
        "https://southfulton.novusagenda.com/agendapublic/meetingsresponsive.aspx"
    ]

    def parse(self, response):
        for item in response.css("tr")[1:]:
            try:
                (
                    _,
                    date,
                    meeting_type,
                    location,
                    agenda_html,
                    agenda_pdf,
                    minutes,
                    legal_minutes,
                ) = item.css("td")
            except ValueError:
                continue
            date = date.css("::text").get() + " 4:00pm"
            meeting = Meeting(
                title=meeting_type.css("::text").get(),
                description="",
                classification=self._parse_classification(item),
                start=dateutil.parser.parse(date),
                end=None,
                all_day=False,
                time_notes="Meetings are typically at 4pm, but check agenda once available to be sure.",  # noqa
                location=self._parse_location(location.css("::text").get()),
                links=self._parse_links(
                    agenda_html, agenda_pdf, minutes, legal_minutes
                ),
                source=self._parse_source(response),
            )

            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)

            yield meeting

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return NOT_CLASSIFIED

    def _parse_location(self, item):
        """Parse or generate location."""
        if ", GA" in item:
            name, address = item.split(" - ")
        else:
            address = ""
            name = item
        return {
            "address": address,
            "name": name,
        }

    def _parse_links(self, agenda_html, agenda_pdf, minutes, legal_minutes):
        links = []
        for title, elem in (
            ("Agenda (HTML)", agenda_html),
            ("Agenda (PDF)", agenda_pdf),
            ("Minutes", minutes),
            ("Legal Minutes", legal_minutes),
        ):
            href = elem.xpath(".//a/@href").get()
            if href:
                links.append(
                    {
                        "href": "https://southfulton.novusagenda.com/agendapublic/"
                        + href,
                        "title": title,
                    }
                )
        return links

    def _parse_source(self, response):
        """Parse or generate source."""
        return response.url
