{
    "name": "Project Scrum",
    "summary": """Scrum sprint management.""",
    "description": """Scrum sprint management.""",
    "author": "Victor Laskurain",
    "license": "AGPL-3",
    "website": "https://github.com/victorlaskurain",
    "category": "Services/Project",
    "version": "16.0.1.0.0",
    # any module necessary for this one to work correctly
    "depends": [
        "base",
        "project",
        "hr_timesheet",
        "line_chart_widget",
        "mail",
        "resource_daily",
    ],
    # always loaded
    "data": [
        "security/project_scrum_security.xml",
        "security/ir.model.access.csv",
        "views/scrum_sprint_views.xml",
        "views/project_task_views.xml",
        "views/project_task_estimation_daily_views.xml",
        "views/project_views.xml",
        "wizard/task_estimation_update_wizard.xml",
    ],
    "assets": {
        "mail.assets_messaging": ["project_scrum/static/src/models/*"],
        "web.assets_backend": ["project_scrum/static/src/components/*/*"],
    },
    # only loaded in demonstration mode
    "demo": [
        "demo/demo.xml",
    ],
}
