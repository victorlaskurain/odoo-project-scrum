# Copyright 2023 Victor Laskurain
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api


class Estimation(models.Model):
    _name = "project.task.estimation"
    _description = (
        "Task Estimation.\n"
        "Holds the expected hours to finalization for a task at a specifict date"
    )

    user_id = fields.Many2one(
        "res.users", help="User who made this estimation", required=True
    )
    task_id = fields.Many2one("project.task", required=True, index=True)
    planned_hours = fields.Float(required=True)


class Task(models.Model):
    _inherit = "project.task"

    estimation_ids = fields.One2many("project.task.estimation", "task_id")
