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
    "depends": ["base", "project", "hr_timesheet", "line_chart_widget"],
    # always loaded
    "data": [
        "security/project_scrum_security.xml",
        "security/ir.model.access.csv",
        "views/scrum_sprint_views.xml",
        "views/project_task_views.xml",
        "views/project_task_estimation_daily_views.xml",
        "wizard/task_estimation_update_wizard.xml",
    ],
    # only loaded in demonstration mode
    "demo": [
        "demo/demo.xml",
    ],
}
