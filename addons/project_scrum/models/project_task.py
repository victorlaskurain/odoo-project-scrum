# Copyright 2023 Victor Laskurain
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class Task(models.Model):
    _inherit = "project.task"

    estimation_ids = fields.One2many("project.task.estimation", "task_id")
    planned_hours_latest = fields.Float(
        "Current estimation",
        tracking=True,
        compute="_compute_planned_hours_latest",
        store=True,
    )

    @api.depends("planned_hours")
    def _compute_planned_hours_latest(self):
        # only used to compute the initial value whenever planned_hours is set
        for task in self.filtered(lambda t: t.planned_hours_latest == False):
            task.planned_hours_latest = task.planned_hours

    def action_update_estimation(self):
        self.ensure_one()
        wizard = self.env["task.estimation.update.wizard"].create(
            {
                "task_id": self.id,
                "planned_hours": self.planned_hours_latest,
                "stage_id": self.project_id.stage_id.id
                if self.env.user.has_group("project.group_project_stages")
                else False,
            }
        )
        return {
            "name": _("Update task %(task_name)s estimation")
            % {"task_name": self.name},
            "view_mode": "form",
            "res_model": "task.estimation.update.wizard",
            "res_id": wizard.id,
            "type": "ir.actions.act_window",
            "target": "new",
        }

    def _message_create(self, values_list):
        # works together with task.estimation.update.wizard to log
        # messages at any point in time. Used basically for testing.
        res = super()._message_create(values_list)
        values = self.env.cr.precommit.data.get(
            "mail.tracking.message.values.project.task", {}
        )
        res.write(values)
        return res

    def _track_finalize_as(self, user_id):
        """Generate tracking message impersonating user_id

        The sole purpose of this method is creating demo records linked to the desired user."""
        return super().with_user(user_id)._track_finalize()
