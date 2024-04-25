from datetime import datetime, timedelta

from city_scrapers_core.constants import CANCELLED, NOT_CLASSIFIED
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider


class AtlDafcSpider(CityScrapersSpider):
    name = "atl_dafc"
    agency = "Development Authority of Fulton County"
    timezone = "America/New_York"
    start_urls = ["https://www.developfultoncounty.com/meetings-and-minutes.php"]

    def parse(self, response):
        this_year = datetime.today().year
        next_year = str(this_year + 1)
        this_year = str(this_year)
        for section in response.css(".table-section.col3.cushycms"):
            section_title = section.css("h1::text").get()
            if not section_title or not (
                this_year in section_title or next_year in section_title
            ):
                continue

            the_year = this_year if this_year in section_title else next_year
            jdama = True if "JDAMA" in section_title else False
            for item in section.css("tr"):
                tds = []
                for td in item.css("td"):
                    links = td.css("a::attr(href)")
                    for link in links:
                        link_href = link.get().strip()
                        link_text = link.css("a::text").get()
                        link_text = link_text.strip() if link_text else ""
                        tds.append((link_text, response.urljoin(link_href)))
                    if not links:
                        text = "".join(td.css("::text").getall())
                        text = text.replace("\xa0", " ").strip() if text else ""
                        tds.append(text)
                if tds:
                    if type(tds[0]) is not str:
                        continue
                    if "diem" not in tds[0].lower():
                        meeting = Meeting(
                            title=self._parse_title(jdama),
                            description=self._parse_description(item),
                            classification=self._parse_classification(item),
                            start=self._parse_start(tds[0], the_year),
                            end=self._parse_end(tds[0], the_year),
                            all_day=False,
                            time_notes=self._parse_time_notes(item),
                            location=self._parse_location(item),
                            links=self._parse_links(tds),
                            source=self._parse_source(response),
                        )

                        cancelled = False
                        for td in tds:
                            search = td[0] if type(td) is tuple else td
                            if "canceled" in search.lower():
                                cancelled = True
                                break

                        meeting["status"] = (
                            self._get_status(meeting) if not cancelled else CANCELLED
                        )
                        meeting["id"] = self._get_id(meeting)

                        yield meeting

    def _parse_title(self, jdama):
        """Parse or generate meeting title."""
        return (
            "Development Authority of Fulton County Meeting"
            if not jdama
            else "Development Authority of Fulton County JDAMA Meeting"
        )

    def _parse_description(self, item):
        """Parse or generate meeting description."""
        return ""

    def _parse_classification(self, item):
        """Parse or generate classification from allowed options."""
        return NOT_CLASSIFIED

    def _parse_start(self, item, the_year):
        try:
            date = datetime.strptime(f"{the_year} {item}", "%Y %B %d %I:%M%p EST")
        except ValueError:
            try:
                date = datetime.strptime(f"{the_year} {item}", "%Y %B %d %I:%M %p EST")
            except ValueError:
                date = datetime.strptime(
                    f"{the_year} {item} 11:30AM EST", "%Y %B %d %I:%M%p EST"
                )
        return date

    def _parse_end(self, item, the_year):
        return self._parse_start(item, the_year) + timedelta(hours=2)

    def _parse_time_notes(self, item):
        return "End time seems to vary between 30 minutes to 2 hours after start"

    def _parse_location(self, item):
        return {
            "address": "141 Pryor Street SW, 2nd Floor Conference Room, "
            "Suite 2052 (Peachtree Level), Atlanta, Georgia 30303",
            "name": "Fulton County Government Administration Building",
        }

    def _parse_links(self, item):
        headers = (
            "Meeting Date & Time",
            "Preliminary Agenda & Fact Sheet",
            "Per Diem",
            "Resolutions",
            "Agenda",
            "Actions",
            "Minutes",
        )
        links = [
            {
                "href": "mailto:doris.coleman@fultoncountyga.gov",
                "title": "Contact Doris M. Coleman for questions regarding meetings",
            }
        ]
        zoom_already = False
        for i in range(len(item)):
            if type(item[i]) is tuple:
                if "zoom" in item[i][1]:
                    if not zoom_already:
                        title = "Zoom link"
                        zoom_already = True
                    else:
                        continue
                else:
                    title = headers[i]
                links.append({"href": item[i][1], "title": title})
        return links

    def _parse_source(self, response):
        return response.url
