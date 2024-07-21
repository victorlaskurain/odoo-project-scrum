# Copyright 2023 Victor Laskurain
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _


class Estimation(models.Model):
    _name = "project.task.estimation"
    _description = (
        "Task Estimation.\n"
        "Holds the expected hours to finalization for a task at a specifict date"
    )
    _auto = False
    _log_access = True  # Include magic fields

    user_id = fields.Many2one(
        "res.users", readonly=True, help="User who made this estimation"
    )
    task_id = fields.Many2one("project.task", readonly=True)
    date = fields.Datetime("Date", readonly=True)
    mail_message_id = fields.Many2one("mail.message", readonly=True)
    planned_hours = fields.Float(required=True, readonly=True)

    def init(self):
        self.env.cr.execute(
            """
CREATE OR REPLACE VIEW %(table)s AS (
    SELECT mtv.id,
           mtv.create_uid,
           mtv.create_date,
           mtv.write_uid,
           mtv.write_date,
           mtv.create_uid      AS user_id,
           mtv.mail_message_id,
           mtv.new_value_float AS planned_hours,
           mm.res_id           AS task_id,
           mm.date             AS date
    FROM       mail_tracking_value AS mtv
    INNER JOIN mail_message        AS mm
            ON mtv.mail_message_id = mm.id
    WHERE field IN (
        SELECT id
        FROM ir_model_fields
        WHERE name = 'planned_hours_latest'
          AND model = 'project.task'
    )
)
"""
            % {"table": self._table}
        )


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
                "stage_id": self.project_id.stage_id.id if self.env.user.has_group('project.group_project_stages') else False,
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
