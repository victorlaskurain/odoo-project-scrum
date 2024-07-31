# Copyright 2024 Victor Laskurain
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class Project(models.Model):
    _inherit = "project.project"

    sprint_ids = fields.One2many("scrum.sprint", "project_id")
    sprint_count = fields.Integer(compute="_compute_sprint_count")

    @api.depends("sprint_ids")
    def _compute_sprint_count(self):
        Sprint = self.env["scrum.sprint"]
        for project in self:
            project.sprint_count = Sprint.search_count(
                [("project_id", "=", project.id)]
            )
