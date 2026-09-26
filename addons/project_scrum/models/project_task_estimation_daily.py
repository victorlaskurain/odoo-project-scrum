# Copyright 2023 Victor Laskurain
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields


class EstimationDaily(models.Model):
    _name = "project.task.estimation.daily"
    _description = (
        "Task Estimation expanded to every day.\n"
        "Holds the expected hours to finalization for a task at a specifict date "
        "or the latest known estimation if that specific date didn't get an "
        "updated estimation. It's an intermediate model, not shown by default "
        "because it's just a stepping stone to build the burndown chart."
    )
    _auto = False
    _log_access = False

    task_id = fields.Many2one("project.task", readonly=True)
    date = fields.Datetime("Date", readonly=True)
    planned_hours = fields.Float(readonly=True)

    def init(self):
        # drops the function, aggregate and the view because of "CASCADE"
        self.env.cr.execute(
            """
DROP FUNCTION IF EXISTS COALESCE_AGG_sfunc(state ANYELEMENT, value ANYELEMENT) CASCADE;
"""
        )
        self.env.cr.execute(
            """
CREATE OR REPLACE VIEW %(table)s AS (
    SELECT ('x'||substr(MD5(task_id::text || day::text), 1, 8))::bit(32)::bigint AS id,
           ssp.task_id AS task_id,
           day::date AS date,
           te.planned_hours AS planned_hours,
            -- esta columna no está en el modelo, se usa en la vista de burndown
           ssp.sprint_id AS sprint_id
    FROM       scrum_sprint_task AS ssp
    INNER JOIN scrum_sprint AS sp ON sp.id = ssp.sprint_id
    INNER JOIN ir_model_fields AS f ON f.name = 'planned_hours_latest' AND f.model = 'project.task'
    CROSS JOIN GENERATE_SERIES(sp.date_begin, sp.date_end + 1, '1 DAY') AS day
    LEFT JOIN LATERAL (
        SELECT new_value_float AS planned_hours
        FROM mail_message AS mm
        INNER JOIN mail_tracking_value AS mtv ON mtv.mail_message_id = mm.id
        WHERE model = 'project.task' AND field = f.id
          AND mm.res_id = ssp.task_id AND mm.date::date <= day.date
        ORDER BY mm.date DESC
        LIMIT 1
    ) AS te ON TRUE
);
"""
            % {"table": self._table}
        )
