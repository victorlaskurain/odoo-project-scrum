# Copyright 2026 Victor Laskurain
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, tools

import logging

_logger = logging.getLogger(__name__)


class TaskEstimationUpdateWizard(models.TransientModel):
    _name = "add.to.scrum.sprint.wizard"

    scrum_sprint_id = fields.Many2one(
        "scrum.sprint", domain=[("is_open", "=", True)], required=True
    )
    task_ids = fields.Many2many("project.task")

    def action_add_to_sprint(self):
        self.ensure_one()
        _logger.info(["bittor", self, self.scrum_sprint_id, self.task_ids])
        sprint = self.scrum_sprint_id
        next_sequence = 1 + max(sprint.sprint_task_ids.mapped("sequence"))
        current_tasks = sprint.sprint_task_ids.mapped("task_id")
        new_tasks = self.task_ids - current_tasks
        self.env["scrum.sprint.task"].create(
            [
                {
                    "sprint_id": sprint.id,
                    "task_id": t.id,
                    "sequence": next_sequence + t.sequence,
                }
                for t in new_tasks
            ]
        )
