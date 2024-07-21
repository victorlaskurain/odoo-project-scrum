# Copyright 2023 Victor Laskurain
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, tools


class TaskEstimationUpdateWizard(models.TransientModel):
    _name = "task.estimation.update.wizard"
    _description = (
        "Task Estimation Update Wizard.\n"
        "Set new estimation and its justification for a task"
    )

    task_id = fields.Many2one("project.task", required=True)
    project_id = fields.Many2one(related="task_id.project_id")
    message = fields.Html("Message")
    planned_hours = fields.Float(required=True)
    stage_id = fields.Many2one(
        "project.task.type",
        string="Stage",
        domain="[('project_ids', '=', project_id)]",
    )

    def action_save(self, date=None):
        self.ensure_one()
        if date != None:
            values = self.env.cr.precommit.data.setdefault(
                "mail.tracking.message.values.project.task", {}
            )
            values["date"] = date
        msg = self.message
        update = {}

        currenth = self.task_id.planned_hours_latest
        newh = self.planned_hours
        estimation_updated = (
            fields.Float.compare(currenth, newh, precision_digits=2) != 0
        )
        if estimation_updated:
            update["planned_hours_latest"] = newh

        currents = self.task_id.stage_id
        news = self.stage_id
        stage_updated = news and currents != news
        if stage_updated:
            update["stage_id"] = news.id

        if update:
            self.task_id.write(update)
            self.task_id._track_set_log_message(msg)
        elif msg:
            self.task_id.message_post(body=msg)
