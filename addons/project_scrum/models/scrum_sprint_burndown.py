# Copyright 2023 Victor Laskurain
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields


class ScrumSprintBurndown(models.Model):
    _name = "scrum.sprint.burndown"
    _description = "Sprint Burndown Chart Data"
    _order = "sprint_id, date"
    _auto = False

    sprint_id = fields.Many2one("scrum.sprint", required=True, readonly=True)
    date = fields.Date(required=True, readonly=True)
    planned_hours = fields.Float(required=True, readonly=True)
    available_hours = fields.Float(required=True, readonly=True)

    def init(self):
        self.env.cr.execute(
            """
DROP VIEW IF EXISTS scrum_sprint_burndown;
CREATE VIEW scrum_sprint_burndown AS (
    WITH sprint_reference AS (
        SELECT sprint_id,
               date::date,
               SUM(dedication) AS hours
        FROM scrum_sprint_developer_dedication_daily
        GROUP BY sprint_id, date::date
    ), sprint_estimation AS (
        SELECT sprint_id,
               date::date,
               SUM(planned_hours) AS hours
        FROM       scrum_sprint_task AS sst
        INNER JOIN project_task_estimation_daily AS pted
                ON sst.task_id = pted.task_id
        GROUP BY sst.sprint_id, pted.date::date
    )
    SELECT reference.sprint_id * 10000
           + RANK() OVER (PARTITION BY reference.sprint_id ORDER BY reference.date) AS id,
           reference.sprint_id,
           reference.date,
           estimation.hours AS planned_hours,
           SUM(reference.hours) OVER (
               PARTITION BY reference.sprint_id
               ORDER BY reference.date DESC
           ) AS available_hours
    FROM       scrum_sprint     AS sprint
    INNER JOIN sprint_reference AS reference
            ON sprint.id = reference.sprint_id
    LEFT  JOIN sprint_estimation AS estimation
            ON estimation.sprint_id = reference.sprint_id
               AND estimation.date = reference.date
    -- remove any day with no activity  but always keep the one that the sprint begins
    WHERE reference.date = sprint.date_begin OR reference.hours > 0
);
"""
        )
