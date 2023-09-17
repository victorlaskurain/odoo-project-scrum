# Copyright 2023 Victor Laskurain
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import models, fields, api, _

_logger = logging.getLogger(__name__)


class SprintDeveloperDedication(models.Model):
    _name = "scrum.sprint.developer.dedication"
    _description = (
        "Developer's dedication to sprint.\n"
        "Holds the dedication (% of her time) of any given developer in this sprint."
    )

    name = fields.Char(related="user_id.name")
    sprint_id = fields.Many2one("scrum.sprint", required=True, index=True)
    user_id = fields.Many2one("res.users", required=True, index=True)
    dedication = fields.Float(required=True, default=1.0)

    _sql_constraints = [
        (
            "dedication_is_valid",
            "CHECK(dedication >= 0 AND dedication <= 1)",
            "Dedication must be between 0% and 100%",
        ),
        (
            "unique_sprint_id_user_id",
            "UNIQUE(sprint_id, user_id)",
            "You can add a user to sprint only once.",
        ),
    ]


class SprintDeveloperDedicationDaily(models.Model):
    _name = "scrum.sprint.developer.dedication.daily"
    _description = (
        "Developer's dedication to sprint (daily).\n"
        "Holds the dedication (number of hours) of any given developer in a "
        "specific day of this sprint."
    )

    sprint_id = fields.Many2one("scrum.sprint", required=True, index=True)
    user_id = fields.Many2one("res.users", required=True, index=True)
    date = fields.Date(required=True)
    dedication = fields.Float(required=True, default=0.0)

    _sql_constraints = [
        (
            "unique_sprint_id_user_id",
            "UNIQUE(sprint_id, user_id, date)",
            "You can add a user to sprint day only once.",
        ),
    ]


class SprintTask(models.Model):
    _name = "scrum.sprint.task"
    _order = "sequence, priority, id DESC"
    _inherits = {"project.task": "task_id"}
    _description = (
        "Sprint Task.\n"
        "This records hold the priority of any given task as part of a sprint. "
        "A given task can be part of multiple sprints and it's priority can vary "
        "from one sprint to the next."
    )

    sprint_id = fields.Many2one("scrum.sprint", required=True, index=True)
    task_id = fields.Many2one(
        "project.task", required=True, index=True, ondelete="cascade"
    )
    sequence = fields.Integer(
        required=True, default=lambda self: self._default_sequence()
    )
    user_id = fields.Many2one("res.users", group_expand="_group_expand_user_id")

    _sql_constraints = [
        (
            "unique_sprint_id_task_id",
            "UNIQUE(sprint_id, task_id)",
            "You can add a task to sprint only once.",
        ),
    ]

    @api.constrains("task_id", "sprint_id")
    def _check_task_in_single_active_sprint(self):
        self.mapped("sprint_id")._check_task_in_single_active_sprint()

    def _default_sequence(self):
        return self.task_id.sequence

    # show a column for each user assigned to the sprint
    def _group_expand_user_id(self, users, domain, order):
        sprint_id = False
        if self.env.context.get("active_model") == "scrum.sprint":
            sprint_id = self.env.context.get("active_id")
        if sprint_id:
            users = (
                self.env["scrum.sprint.developer.dedication"]
                .search([("sprint_id", "=", sprint_id)])
                .mapped("user_id")
            )
        return users

    def action_edit_task(self):
        return {
            "type": "ir.actions.act_window",
            "res_model": "project.task",
            "res_id": self.task_id.id,
            "view_mode": "form",
        }

    def action_update_estimation(self):
        return self.task_id.action_update_estimation()


class Sprint(models.Model):
    _name = "scrum.sprint"
    _description = (
        "Scrum Sprint.\n"
        "A scrum sprint represents a set of tasks expected to be accomplished "
        "by a set of developers during an specific date range. Often a sprint "
        "will belong to a given project but this is not required so that taking "
        "care of task from different project in the same sprint is possible."
    )
    _inherit = ["mail.thread.cc", "mail.activity.mixin"]

    _sql_constraints = [
        (
            "date_range_valid",
            "CHECK(date_begin <= date_end)",
            "A sprint cannot end before it begins.",
        )
    ]

    name = fields.Char(required=True)
    project_id = fields.Many2one(
        "project.project", required=False, domain="[('company_id', '=', company_id)]"
    )
    company_id = fields.Many2one(
        "res.company",
        string="Company",
        required=True,
        default=lambda self: self.env.company,
    )
    scrum_master_user_id = fields.Many2one(
        "res.users",
        string="Scrum master",
        required=True,
        domain="[('company_id', '=', company_id)]",
    )
    developer_dedication_ids = fields.One2many(
        "scrum.sprint.developer.dedication", "sprint_id", string="Developer Dedication"
    )
    developer_dedication_daily_ids = fields.One2many(
        "scrum.sprint.developer.dedication.daily",
        "sprint_id",
        compute="_compute_developer_dedication_daily_ids",
        compute_sudo=True,
        string="Developer Dedication per Day",
        store=True,
    )
    developer_ids = fields.Many2many(
        "res.users",
        compute="_compute_developer_ids",
        search="_search_developer_ids",
        string="Developers",
    )
    date_begin = fields.Date(
        required=True,
        index=True,
        tracking=10,
        string="Begins",
        help="This day work on this sprint starts",
    )
    date_end = fields.Date(
        required=True,
        index=True,
        tracking=20,
        string="Ends",
        help="This day the sprint is done.",
    )
    sprint_task_ids = fields.One2many("scrum.sprint.task", "sprint_id")
    sprint_task_count = fields.Integer(compute="_compute_sprint_task_count")
    velocity_estimated = fields.Float(required=True, default=1.0)
    state = fields.Selection(
        selection=[
            ("draft", "Pending"),
            ("in_progress", "In progress"),
            ("closed", "Closed"),
        ],
        default="draft",
        tracking=30,
    )  # :TODO: compute from dates
    active = fields.Boolean(default=True)

    @api.depends("developer_dedication_ids")
    def _compute_developer_ids(self):
        for sprint in self:
            sprint.developer_ids = sprint.developer_dedication_ids.mapped("user_id")

    def _search_developer_ids(self, operator, value):
        return [("developer_dedication_ids.user_id", operator, value)]

    @api.depends(
        "developer_dedication_ids",
        "developer_dedication_ids.dedication",
        "date_begin",
        "date_end",
    )
    def _compute_developer_dedication_daily_ids(self):
        # just recompute all the data from scratch.
        self.env.flush_all()
        self.env.cr.execute(
            """
DELETE FROM scrum_sprint_developer_dedication_daily
WHERE sprint_id IN %(sprint_ids)s;

INSERT INTO scrum_sprint_developer_dedication_daily (sprint_id, user_id, date, dedication)
    SELECT ss.id, ssdd.user_id, rda.date, rda.availability_hours * ssdd.dedication
    FROM       scrum_sprint AS ss
    INNER JOIN scrum_sprint_developer_dedication AS ssdd
            ON ss.id = ssdd.sprint_id
    INNER JOIN hr_employee AS hre
            ON hre.user_id = ssdd.user_id
               AND hre.company_id = ss.company_id
    INNER JOIN resource_daily_availability AS rda
            ON rda.resource_id = hre.resource_id
               AND rda.date BETWEEN ss.date_begin AND ss.date_end
    WHERE ss.id IN %(sprint_ids)s
    -- this is redundant but helps the planner A LOT: the simple case
    -- of a single sprint for a single developer and a month of sprint
    -- duration time falls from 5s to 2ms!!!
          AND rda.date BETWEEN %(date_begin)s AND %(date_end)s;
""",
            {
                "sprint_ids": tuple(self.ids + [-1]),
                "date_begin": min(self.mapped("date_begin")),
                "date_end": max(self.mapped("date_end")),
            },
        )
        self.env.invalidate_all()

    @api.depends("sprint_task_ids")
    def _compute_sprint_task_count(self):
        for sprint in self:
            sprint.sprint_task_count = self.env["scrum.sprint.task"].search_count(
                [("sprint_id", "=", sprint.id)]
            )

    @api.constrains("date_begin", "date_end")
    def _check_task_in_single_active_sprint(self):
        cr = self.env.cr
        for rec in self:
            # (-1,) + ... prevents empty task_ids lists
            task_ids = (-1,) + tuple(rec.sprint_task_ids.mapped("task_id").mapped("id"))
            date_begin = rec.date_begin
            date_end = rec.date_end
            cr.execute(
                """
SELECT ss.id AS sprint_id,
       sst.task_id AS task_id
FROM       scrum_sprint       AS ss
INNER JOIN scrum_sprint_task AS sst
        ON sst.sprint_id = ss.id
WHERE NOT ss.active
      AND GREATEST(ss.date_begin, %(date_begin)s) < LEAST(ss.date_end, %(date_end)s)
      AND sst.task_id IN %(task_ids)s
""",
                locals(),
            )
            overlap = cr.fetchall()
            if len(overlap) > 1:
                # :TODO: make message more useful by indicate which tasks and sprints
                raise ValidationError(_("Some task is included in two active sprints"))

    def action_show_tasks(self):
        self.ensure_one()
        return {
            "name": _("Tasks"),
            "type": "ir.actions.act_window",
            "res_model": "scrum.sprint.task",
            "domain": [("sprint_id", "=", self.id)],
            "view_mode": "kanban,tree",
        }


class ScrumSprintBurndown(models.Model):
    _name = "scrum.sprint.burndown"
    _description = "Sprint Burndown Chart Data"
    _auto = False
