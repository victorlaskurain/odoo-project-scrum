{
    "name": "Resource Daily",
    "summary": """Daily resource availability and usage views.""",
    "description": """
Provides expanded daily views of the resource calendar and attendance models so
that you can compute any resource's usage at the SQL level.""",
    "author": "Victor Laskurain",
    "license": "AGPL-3",
    "website": "https://github.com/victorlaskurain",
    "category": "Hidden",
    "version": "16.0.1.0.0",
    # any module necessary for this one to work correctly
    "depends": ["resource", "base_setup"],
    # always loaded
    "data": [
        "security/ir.model.access.csv",
        "views/resource_daily_availability.xml",
        "views/res_config_settings_views.xml",
    ],
    # only loaded in demonstration mode
    "demo": [
        "demo/resource_calendar_demo.xml",
    ],
}
