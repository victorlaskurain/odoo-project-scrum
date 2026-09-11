# Copyright 2026 Victor Laskurain
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import timedelta

from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestProjectTask(TransactionCase):
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

    def _add_task_to_sprint(self, sprint, task):
        return self.env["scrum.sprint.task"].create(
            {
                "sprint_id": sprint.id,
                "task_id": task.id,
            }
        )

    def test_sprint_count_is_zero_when_task_is_not_in_any_sprint(self):
        task = self._create_task("Standalone")
        self.assertEqual(task.sprint_count, 0)
        self.assertFalse(task.sprint_ids)

    def test_sprint_count_and_ids_follow_sprint_tasks(self):
        task = self._create_task("In two sprints")
        self._add_task_to_sprint(self.open_sprint, task)
        self.assertEqual(task.sprint_count, 1)
        self.assertEqual(task.sprint_ids, self.open_sprint)

        self._add_task_to_sprint(self.closed_sprint, task)
        self.assertEqual(task.sprint_count, 2)
        self.assertEqual(task.sprint_ids, self.open_sprint | self.closed_sprint)

    def test_action_view_sprints_opens_form_when_there_is_one(self):
        task = self._create_task("Single sprint")
        self._add_task_to_sprint(self.open_sprint, task)

        action = task.action_view_sprints()

        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "scrum.sprint")
        self.assertEqual(action["view_mode"], "form")
        self.assertEqual(action["res_id"], self.open_sprint.id)
        self.assertEqual(action["views"], [(False, "form")])

    def test_action_view_sprints_opens_list_when_there_are_several(self):
        task = self._create_task("Several sprints")
        self._add_task_to_sprint(self.open_sprint, task)
        self._add_task_to_sprint(self.closed_sprint, task)

        action = task.action_view_sprints()

        self.assertEqual(action["type"], "ir.actions.act_window")
        self.assertEqual(action["res_model"], "scrum.sprint")
        self.assertEqual(action["view_mode"], "kanban,tree,form")
        self.assertNotIn("res_id", action)
        self.assertEqual(action["domain"][0][0], "id")
        self.assertEqual(action["domain"][0][1], "in")
        self.assertEqual(
            set(action["domain"][0][2]),
            set((self.open_sprint | self.closed_sprint).ids),
        )
