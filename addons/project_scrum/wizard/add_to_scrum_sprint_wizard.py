# Copyright 2026 Victor Laskurain
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields, models


class AddToScrumSprintWizard(models.TransientModel):
    _name = "add.to.scrum.sprint.wizard"
    _description = "Add Tasks to Sprint"

    scrum_sprint_id = fields.Many2one(
        "scrum.sprint",
        string="Sprint",
        domain=[("is_open", "=", True)],
        required=True,
    )
    task_ids = fields.Many2many("project.task")

    def action_add_to_sprint(self):
        """Append selected tasks to the sprint and open its task list."""
        self.ensure_one()
        sprint = self.scrum_sprint_id
        current_tasks = sprint.sprint_task_ids.mapped("task_id")
        new_tasks = self.task_ids - current_tasks
        next_sequence = max(sprint.sprint_task_ids.mapped("sequence"), default=0) + 1
        self.env["scrum.sprint.task"].create(
            [
                {
                    "sprint_id": sprint.id,
                    "task_id": task.id,
                    "sequence": next_sequence + index,
                }
                for index, task in enumerate(new_tasks)
            ]
        )
        return sprint.action_show_tasks()
