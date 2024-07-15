import json

import scrapy
from city_scrapers_core.constants import BOARD
from city_scrapers_core.items import Meeting
from city_scrapers_core.spiders import CityScrapersSpider
from dateutil.parser import parse as parse_date


class AtlDekalbCountyBoeSpider(CityScrapersSpider):
    name = "atl_dekalb_county_boe"
    agency = "DeKalb County Board of Education"
    timezone = "America/New_York"
    source = "https://simbli.eboardsolutions.com/SB_Meetings/SB_MeetingListing.aspx?S=4054"  # noqa

    def start_requests(self):
        url = (
            "https://simbli.eboardsolutions.com/Services/api/GetMeetingListing"  # noqa
        )
        # Return 50 most recent meetings.
        # ConnectionString and SecurityToken are required.
        body = {
            "ListingType": "0",
            "TimeZone": "0",
            "CustomSort": 0,
            "SortColName": "DateTime",
            "IsSortDesc": True,
            "RecordStart": 0,
            "RecordCount": 50,
            "FilterExp": "",
            "ParentGroup": None,
            "IsUserLoggedIn": False,
            "UserID": "",
            "UserRole": None,
            "EncUserId": None,
            "Id": 0,
            "SchoolID": "4054",
            "ConnectionString": "Z6PDprZMNLXHjSBXkCx3nyYUcSP5M6UnadUK7cjlwACaJqjO6BIZp9WiwanwbY4ZVnjRygpzATee7Qu0w1S8HmAR37HwZBl63V1gla1aplusJUjsbp3RPOgYD8rKMge0DRnjghPLCYcGBvWfEYLDJCwhuND0gFm8zDEltMnSkGHH8U=",  # noqa
            "SecurityToken": "ZekKE44z6voP8TArAiQr1KqQ7APJMDvo3Mr5tEPYHAow2XgYXKhCVFLu2pHhFaTMoGVOGKg8vFV2Yz70u3sDLEVU4nY7qDAdNvoAJgGmnzjBEfmMTseZAXEzpY4u1Boz",  # noqa
            "CreatedOn": "0001-01-01T00:00:00",
            "CreatedBy": None,
            "ModifiedOn": "0001-01-01T00:00:00",
            "ModifiedBy": None,
            "DeletedBy": None,
            "DeletedOnUTC": None,
            "IsDeleted": False,
        }
        serialized_body = json.dumps(body)
        yield scrapy.Request(
            url,
            method="POST",
            body=serialized_body,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json",
            },
        )

    def parse(self, response):
        data = response.json()
        # write to file
        with open("dekalb.json", "w") as f:
            json.dump(data, f)
        for item in data:
            start = parse_date(item["MM_DateTime"])
            location = {
                "name": item["MM_Address1"],
                "address": f"{item['MM_Address2']} {item['MM_Address3']}",
            }
            meeting = Meeting(
                title=item["MM_MeetingTitle"],
                description="",
                classification=BOARD,
                start=start,
                end=None,
                all_day=False,
                time_notes="",
                location=location,
                links=[],
                source=self.source,
            )
            meeting["status"] = self._get_status(meeting)
            meeting["id"] = self._get_id(meeting)
            yield meeting
