# Copyright 2026 Victor Laskurain
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestAddToScrumSprint(TransactionCase):
    def setUp(self):
        super().setUp()
        Project = self.env["project.project"]
        self.project = Project.create({"name": "Sprint Test Project"})
        today = fields.Date.today()
        self.open_sprint = self._create_sprint(
            date_begin=today,
            date_end=today + timedelta(days=14),
        )
        self.closed_sprint = self._create_sprint(
            date_begin=today - timedelta(days=28),
            date_end=today - timedelta(days=1),
        )

    def _create_sprint(self, **vals):
        values = {
            "scrum_master_user_id": self.env.user.id,
            "date_begin": fields.Date.today(),
            "date_end": fields.Date.today(),
        }
        values.update(vals)
        return self.env["scrum.sprint"].create(values)

    def _create_task(self, name):
        return self.env["project.task"].create(
            {
                "name": name,
                "project_id": self.project.id,
            }
        )

    def _add_to_sprint(self, sprint, tasks):
        wizard = self.env["add.to.scrum.sprint.wizard"].create(
            {
                "scrum_sprint_id": sprint.id,
                "task_ids": [(6, 0, tasks.ids)],
            }
        )
        return wizard.action_add_to_sprint()

    def test_add_tasks_appended_at_the_end(self):
        """New tasks are added after the tasks already in the sprint."""
        existing_task = self._create_task("Existing")
        self.env["scrum.sprint.task"].create(
            {
                "sprint_id": self.open_sprint.id,
                "task_id": existing_task.id,
                "sequence": 10,
            }
        )
        first_task = self._create_task("First new")
        second_task = self._create_task("Second new")

        self._add_to_sprint(self.open_sprint, first_task | second_task)

        sprint_tasks = self.open_sprint.sprint_task_ids.sorted("sequence")
        self.assertEqual(
            sprint_tasks.mapped("task_id"),
            existing_task | first_task | second_task,
        )
        self.assertEqual(sprint_tasks[0].sequence, 10)
        self.assertEqual(sprint_tasks[1].sequence, 11)
        self.assertEqual(sprint_tasks[2].sequence, 12)

    def test_add_tasks_to_empty_sprint(self):
        """Tasks can be added when the sprint has no tasks yet."""
        task = self._create_task("Only task")

        self._add_to_sprint(self.open_sprint, task)

        self.assertEqual(self.open_sprint.sprint_task_ids.task_id, task)
        self.assertEqual(self.open_sprint.sprint_task_ids.sequence, 1)

    def test_does_not_duplicate_existing_tasks(self):
        """A task already in the sprint is not added again."""
        task = self._create_task("Already in sprint")
        self.env["scrum.sprint.task"].create(
            {
                "sprint_id": self.open_sprint.id,
                "task_id": task.id,
                "sequence": 5,
            }
        )

        self._add_to_sprint(self.open_sprint, task)

        self.assertEqual(len(self.open_sprint.sprint_task_ids), 1)
        self.assertEqual(self.open_sprint.sprint_task_ids.sequence, 5)

    def test_returns_sprint_tasks_action(self):
        """Confirming the wizard opens the same action as the sprint tasks button."""
        task = self._create_task("New task")
        expected = self.open_sprint.action_show_tasks()

        action = self._add_to_sprint(self.open_sprint, task)

        self.assertEqual(action["type"], expected["type"])
        self.assertEqual(action["res_model"], expected["res_model"])
        self.assertEqual(action["domain"], expected["domain"])
        self.assertEqual(action["view_mode"], expected["view_mode"])
        self.assertEqual(action["context"], expected["context"])

    def test_only_unfinished_sprints_are_selectable(self):
        """The sprint field only lists sprints whose end date is not in the past."""
        domain = (
            self.env["add.to.scrum.sprint.wizard"]._fields["scrum_sprint_id"].domain
        )
        sprints = self.env["scrum.sprint"].search(domain)

        self.assertIn(self.open_sprint, sprints)
        self.assertNotIn(self.closed_sprint, sprints)
        self.assertTrue(self.open_sprint.is_open)
        self.assertFalse(self.closed_sprint.is_open)
