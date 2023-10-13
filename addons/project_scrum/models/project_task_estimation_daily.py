# Copyright 2023 Victor Laskurain
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _


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
DROP FUNCTION IF EXISTS COALESCE_AGG_sfunc(state ANYELEMENT, value ANYELEMENT) CASCADE
"""
        )
        self.env.cr.execute(
            """
CREATE FUNCTION COALESCE_AGG_sfunc(state ANYELEMENT, value ANYELEMENT) RETURNS ANYELEMENT AS
$$
    SELECT COALESCE(value, state);
$$ LANGUAGE SQL;
"""
        )
        self.env.cr.execute(
            """
CREATE AGGREGATE COALESCE_AGG(ANYELEMENT) (
    SFUNC = COALESCE_AGG_SFUNC,
    STYPE  = ANYELEMENT
)
"""
        )
        self.env.cr.execute(
            """
CREATE VIEW %(table)s AS (
    WITH date_range AS (
        SELECT MIN(date_begin) AS begin,
               MAX(date_end)   AS end
        FROM scrum_sprint
    ), every_day AS (
        SELECT day::date AS date
        FROM       date_range
        CROSS JOIN GENERATE_SERIES(date_range.begin, date_range.end, '1 DAY') AS day
    ), last_estimation_of_date AS (
        SELECT t.task_id,
               t.date_day AS date,
               t.planned_hours
        FROM (
            SELECT pte.*,
                   date::date AS date_day,
                   LAST_VALUE(id) OVER task_window AS last_id
            FROM project_task_estimation AS pte
            WINDOW task_window AS (
                PARTITION BY pte.task_id, pte.date::date
                ORDER BY pte.date, id
                RANGE BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING
            )
        ) AS t
        WHERE t.id = t.last_id
    ), last_estimation_every_date AS (
        SELECT pt.id AS task_id,
               ed.date,
               COALESCE_AGG(leod.planned_hours) OVER (
                   PARTITION BY pt.id
                   ORDER BY ed.date) AS planned_hours
        FROM       project_task AS pt
        CROSS JOIN every_day    AS ed
        LEFT JOIN last_estimation_of_date AS leod
               ON ed.date = leod.date AND pt.id = leod.task_id
     )
    SELECT
           leed.task_id * 10000
           + RANK() OVER (PARTITION BY leed.task_id ORDER BY leed.date) AS id,
           leed.task_id,
           leed.date,
           leed.planned_hours
    FROM last_estimation_every_date AS leed
)
"""
            % {"table": self._table}
        )
