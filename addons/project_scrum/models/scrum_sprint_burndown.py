# Copyright 2023 Victor Laskurain
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import api, models, fields

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
CREATE OR REPLACE VIEW scrum_sprint_burndown AS (
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
        FROM       project_task_estimation_daily AS pted
        GROUP BY pted.sprint_id, pted.date::date
    )
    SELECT reference.sprint_id * 10000
           + RANK() OVER (PARTITION BY reference.sprint_id ORDER BY reference.date) AS id,
           reference.sprint_id,
           reference.date,
           estimation.hours AS planned_hours,
           SUM(reference.hours)
               FILTER (
                   WHERE reference.date <> sprint.date_end) -- no work done on the sprint en date
               OVER (
                   PARTITION BY reference.sprint_id ORDER BY reference.date DESC
               ) * sprint.velocity_estimated AS available_hours
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

    # optimización salvaje para el caso (muy común) en el que se
    # desean obtener los datos para pintar el gráfico. En search_read
    # se captura el caso específico y se agrega un parámetro en el
    # contexto que luego se lee en _apply_ir_rules. _apply_ir_rules es
    # el único punto en el que podemos modificar la quey que se
    # ejecuta.
    @api.model
    def search_read(
        self, domain=None, fields=None, offset=0, limit=None, order=None, **read_kwargs
    ):
        try:
            assert len(domain) == 1
            [[sprint_id_txt, eq_txt, sprint_id]] = domain
            assert sprint_id_txt == "sprint_id" and eq_txt == "="
            fields_sorted = fields.copy()
            fields_sorted.sort()
            assert fields_sorted == ["available_hours", "date", "planned_hours"]
        except AssertionError: # no estamos en el caso especial
            res = super().search_read(
                domain, fields, offset, limit, order, **read_kwargs
            )
        else:
            res = super(
                ScrumSprintBurndown, self.with_context(search_sprint_id=sprint_id)
            ).search_read(domain, fields, offset, limit, order, **read_kwargs)
        return res

    @api.model
    def _apply_ir_rules(self, query, mode="read"):
        super()._apply_ir_rules(query, mode)
        sprint_id = self._context.get("search_sprint_id")
        if sprint_id:
            query.add_where("sprint_id = %s", (sprint_id,))
