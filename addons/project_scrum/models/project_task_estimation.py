# Copyright 2023 Victor Laskurain
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields


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
