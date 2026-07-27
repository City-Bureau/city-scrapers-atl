from city_scrapers.mixins.atl_clarkston_city_council import (
    AtlClarkstonCityCouncilSpiderMixin,
)

spider_configs = [
    {
        "class_name": "AtlClarkstonCityCouncilSpider",
        "name": "atl_clarkston_city_council",
        "agency": "City of Clarkston City Council",
        "agency_name": "City Council of Clarkston",
        "category_id": ["26", "24"],  # City Council + General combined
    },
    {
        "class_name": "AtlClarkstonCityCouncilPlanningZoningBoardSpider",
        "name": "atl_clarkston_city_council_planning_zoning_board",
        "agency": "City of Clarkston Planning and Zoning Board",
        "agency_name": "City Council of Clarkston",
        "category_id": "27",
    },
    {
        "class_name": "AtlClarkstonCityCouncilHistoricPreservationCommissionSpider",
        "name": "atl_clarkston_city_council_historic_preservation_commission",
        "agency": "City of Clarkston Historic Preservation Commission",
        "agency_name": "City Council of Clarkston",
        "category_id": "28",
    },
    {
        "class_name": "AtlClarkstonCityCouncilDowntownDevelopmentAuthoritySpider",
        "name": "atl_clarkston_city_council_downtown_development_authority",
        "agency_name": "City Council of Clarkston",
        "agency": "City of Clarkston Downtown Development Authority",
        "category_id": "29",
    },
    {
        "class_name": "AtlClarkstonCityCouncilStandingAdvisoryCommitteeSpider",
        "name": "atl_clarkston_city_council_standing_advisory_committee",
        "agency": "City of Clarkston Standing Advisory Committee",
        "agency_name": "City Council of Clarkston",
        "category_id": "30",
    },
]


def create_spiders():
    """
    Dynamically create spider classes using the spider_configs list
    and register them in the global namespace.
    """
    for config in spider_configs:
        class_name = config["class_name"]

        if class_name not in globals():
            attrs = {k: v for k, v in config.items() if k != "class_name"}

            spider_class = type(
                class_name,
                (AtlClarkstonCityCouncilSpiderMixin,),
                attrs,
            )

            globals()[class_name] = spider_class


create_spiders()
