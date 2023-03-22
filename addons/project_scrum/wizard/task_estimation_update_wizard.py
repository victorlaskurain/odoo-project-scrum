# Copyright 2023 Victor Laskurain
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
from odoo import models, fields, api, tools


class TaskEstimationUpdateWizard(models.TransientModel):
    _name = "task.estimation.update.wizard"
    _description = (
        "Task Estimation Update Wizard.\n"
        "Set new estimation and its justification for a task"
    )

    task_id = fields.Many2one("project.task", required=True)
    message = fields.Html("Message")
    planned_hours = fields.Float(required=True)

    def action_save(self):
        self.ensure_one()
        msg = self.message
        currenth = self.task_id.planned_hours_latest
        newh = self.planned_hours
        estimation_updated = (
            fields.Float.compare(currenth, newh, precision_digits=2) != 0
        )
        if estimation_updated:
            self.task_id.planned_hours_latest = newh
            self.task_id._track_set_log_message(msg)
        elif msg:
            self.task_id.message_post(body=msg)
