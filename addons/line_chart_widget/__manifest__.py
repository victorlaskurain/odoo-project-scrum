{
    "name": "Line Chart Widget",
    "summary": """Render One2many fields as line charts""",
    "description": """""",
    "author": "Victor Laskurain",
    "license": "AGPL-3",
    "website": "https://github.com/victorlaskurain",
    "version": "16.0.1.0.0",
    # any module necessary for this one to work correctly
    "depends": ["web"],
    # always loaded
    "data": [],
    "assets": {
        "web.assets_backend": [
            "line_chart_widget/static/src/line_chart_widget.xml",
            "line_chart_widget/static/src/line_chart_widget.js",
        ],
    },
    # only loaded in demonstration mode
    "demo": [],
}
