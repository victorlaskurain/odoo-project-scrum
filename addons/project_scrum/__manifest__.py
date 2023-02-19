{
    "name": "project_scrum",
    "summary": """Scrum sprint management.""",
    "description": """Scrum sprint management.""",
    "author": "Victor Laskurain",
    "license": "AGPL-3",
    "website": "https://github.com/victorlaskurain",
    "category": "Services/Project",
    "version": "16.0.1.0.0",
    # any module necessary for this one to work correctly
    "depends": ["base", "project"],
    # always loaded
    "data": [
        "security/project_scrum_security.xml",
        "security/ir.model.access.csv",
        "views/scrum_sprint_views.xml",
    ],
    # only loaded in demonstration mode
    "demo": [
        "demo/demo.xml",
    ],
}
