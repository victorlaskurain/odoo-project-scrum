# Copyright 2023 Victor Laskurain
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging

from odoo import models, api, fields
from odoo.osv.expression import OR

_logger = logging.getLogger(__name__)


# List on the scrum.sprint chatter all the messages logged into any of
# its tasks
class Message(models.Model):
    _inherit = "mail.message"

    task_id = fields.Many2one("project.task", compute="_compute_task_id")

    @api.depends("model", "res_id")
    def _compute_task_id(self):
        Task = self.env["project.task"]
        for item in self:
            item.task_id = (
                Task.browse(item.res_id) if item.model == "project.task" else False
            )

    # this functions just has _message_format get "task_id" too in its
    # fnames parameter.
    def _get_message_format_fields(self):
        return super()._get_message_format_fields() + ["task_id"]

    # If the call is a request for the messages of a sprint, then:
    #   a) add tasks to the resultset
    #   b) set sprint_id in context for the benefit of _message_format
    @api.model
    def _message_fetch(self, domain, max_id=None, min_id=None, limit=30):
        if domain[1:2] == [("model", "=", "scrum.sprint")]:
            sprint_id = domain[0][2]
            task_ids = (
                self.env["scrum.sprint.task"]
                .search([("sprint_id", "=", sprint_id)])
                .mapped("task_id")
                .ids
            )
            tasks_domain = [
                ("res_id", "in", task_ids),
                ("model", "=", "project.task"),
                ("message_type", "!=", "user_notification"),
            ]
            domain = OR([domain, tasks_domain])
            res = (
                super()
                ._message_fetch(domain, max_id, min_id, limit)
                .with_context(sprint_id=sprint_id)
            )
        else:
            res = super()._message_fetch(domain, max_id, min_id, limit)
        return res

    # format task_id as a JS object with id and name and rename to task.
    def _message_format(self, fnames, format_reply=True, legacy=False):
        sprint_id = self.env.context.get("sprint_id")
        res = super()._message_format(fnames, format_reply, legacy)
        for item in res:
            item["sprint_id"] = sprint_id
            item["task"] = (
                {"id": item["task_id"][0], "name": item["task_id"][1]}
                if item["task_id"]
                else "clear"
            )
            del item["task_id"]
        return res
