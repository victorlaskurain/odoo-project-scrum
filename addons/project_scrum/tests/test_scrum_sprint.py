# Copyright 2023 Victor Laskurain
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestScrumSprint(TransactionCase):
    def setUp(self):
        super().setUp()
        self.project = self.env["project.project"].create(
            {"name": "Sprint Test Project"}
        )

    def test_generate_next_sprint(self):
        """Next sprint copies the current one with shifted dates and unfinished tasks."""
        Task = self.env["project.task"]
        Sprint = self.env["scrum.sprint"]
        date_begin = fields.Date.from_string("2026-01-01")
        date_end = fields.Date.from_string("2026-01-15")
        unfinished_task = Task.create(
            {
                "name": "Unfinished task",
                "project_id": self.project.id,
                "planned_hours": 5,
            }
        )
        finished_task = Task.create(
            {
                "name": "Finished task",
                "project_id": self.project.id,
                "planned_hours": 0,
            }
        )
        sprint = Sprint.create(
            {
                "name": "Sprint 1",
                "project_id": self.project.id,
                "scrum_master_user_id": self.env.user.id,
                "date_begin": date_begin,
                "date_end": date_end,
                "velocity_estimated": 0.8,
                "developer_dedication_ids": [
                    (0, 0, {"user_id": self.env.user.id, "dedication": 0.5}),
                ],
                "sprint_task_ids": [
                    (
                        0,
                        0,
                        {
                            "task_id": unfinished_task.id,
                            "sequence": 10,
                            "user_id": self.env.user.id,
                        },
                    ),
                    (
                        0,
                        0,
                        {
                            "task_id": finished_task.id,
                            "sequence": 20,
                        },
                    ),
                ],
            }
        )

        action = sprint.action_generate_next_sprint()
        next_sprint = Sprint.browse(action["res_id"])

        self.assertEqual(next_sprint.date_begin, date_end)
        self.assertEqual(next_sprint.date_end, fields.Date.from_string("2026-01-29"))
        self.assertNotEqual(next_sprint.name, sprint.name)
        self.assertTrue(next_sprint.name.startswith("SCRUM/"))
        self.assertEqual(next_sprint.project_id, sprint.project_id)
        self.assertEqual(next_sprint.scrum_master_user_id, sprint.scrum_master_user_id)
        self.assertEqual(next_sprint.velocity_estimated, 0.8)
        self.assertEqual(len(next_sprint.developer_dedication_ids), 1)
        self.assertEqual(next_sprint.developer_dedication_ids.user_id, self.env.user)
        self.assertEqual(next_sprint.developer_dedication_ids.dedication, 0.5)
        self.assertEqual(next_sprint.sprint_task_ids.task_id, unfinished_task)
        self.assertEqual(next_sprint.sprint_task_ids.sequence, 10)
        self.assertEqual(next_sprint.sprint_task_ids.user_id, self.env.user)
        self.assertEqual(len(sprint.sprint_task_ids), 2)
        self.assertEqual(action["res_model"], "scrum.sprint")
        self.assertEqual(action["view_mode"], "form")

    def _create_sprint(self, **vals):
        values = {
            "scrum_master_user_id": self.env.user.id,
            "date_begin": fields.Date.from_string("2026-01-01"),
            "date_end": fields.Date.from_string("2026-01-15"),
        }
        values.update(vals)
        return self.env["scrum.sprint"].create(values)

    def test_create_assigns_sequence(self):
        """New sprints without a custom name get the next sequence number."""
        sprint = self._create_sprint()
        self.assertTrue(sprint.name.startswith("SCRUM/"))
        self.assertNotEqual(sprint.name, "New")

    def test_create_keeps_custom_name(self):
        """An explicitly provided name is not replaced by the sequence."""
        sprint = self._create_sprint(name="Sprint 1")
        self.assertEqual(sprint.name, "Sprint 1")

    def test_copy_assigns_sequence(self):
        """Duplicating a sprint assigns a new sequence number as name."""
        sprint = self._create_sprint()
        copy = sprint.copy()
        self.assertTrue(copy.name.startswith("SCRUM/"))
        self.assertNotEqual(copy.name, sprint.name)
        self.assertNotEqual(copy.name, "New")
