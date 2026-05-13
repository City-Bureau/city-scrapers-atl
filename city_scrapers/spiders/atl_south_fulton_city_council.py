from city_scrapers.mixins.atl_south_fulton_city_council import (
    AtlSouthFultonCityCouncilSpiderMixin,
)

spider_configs = [
    {
        "class_name": "AtlSouthFultonCityCouncilSpider",
        "name": "atl_south_fulton_city_council",
        "agency": "South Fulton City Council",
        "category_id": "26",
    },
    {
        "class_name": "AtlSouthFultonGeneralSpider",
        "name": "atl_south_fulton_general",
        "agency": "South Fulton General",
        "category_id": "24",
    },
    {
        "class_name": "AtlSouthFultonDowntownDevelopmentAuthoritySpider",
        "name": "atl_south_fulton_downtown_development_authority",
        "agency": "South Fulton Downtown Development Authority",
        "category_id": "27",
    },
    {
        "class_name": "AtlSouthFultonConventionandVisitorsBureauSpider",
        "name": "atl_south_fulton_convention_and_visitors_bureau",
        "agency": "South Fulton Convention and Visitors Bureau",
        "category_id": "28",
    },
    {
        "class_name": "AtlSouthFultonPlanningCommissionSpider",
        "name": "atl_south_fulton_planning_commission",
        "agency": "South Fulton Planning Commission",
        "category_id": "29",
    },
    {
        "class_name": "AtlSouthFultonZoningBoardofAppealsSpider",
        "name": "atl_south_fulton_zoning_board_of_appeals",
        "agency": "South Fulton Zoning Board of Appeals",
        "category_id": "30",
    },
    {
        "class_name": "AtlSouthFultonPublicArtsCommitteeSpider",
        "name": "atl_south_fulton_public_arts_committee",
        "agency": "South Fulton Public Arts Committee",
        "category_id": "31",
    },
    {
        "class_name": "AtlSouthFultonBoardofCodeEnforcementSpider",
        "name": "atl_south_fulton_board_of_code_enforcement",
        "agency": "South Fulton Board of Code Enforcement",
        "category_id": "32",
    },
    {
        "class_name": "AtlSouthFultonHistoricandCulturalLandmarksCommissionSpider",
        "name": "atl_south_fulton_historic_and_cultural_landmarks_commission",
        "agency": "South Fulton Historic and Cultural Landmarks Commission",
        "category_id": "33",
    },
    {
        "class_name": "AtlSouthFultonCityManagerReviewandApprovalsSpider",
        "name": "atl_south_fulton_city_manager_review_and_approvals",
        "agency": "South Fulton City Manager Review and Approvals",
        "category_id": "34",
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
                (AtlSouthFultonCityCouncilSpiderMixin,),
                attrs,
            )

            globals()[class_name] = spider_class


create_spiders()
