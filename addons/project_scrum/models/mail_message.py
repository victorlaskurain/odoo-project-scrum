# Copyright 2023 Victor Laskurain
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, api, fields
from odoo.orm.domains import Domain

# List on the scrum.sprint chatter all the messages logged into any of
# its tasks
class Message(models.Model):
    _inherit = "mail.message"

    # If the call is a request for the messages of a sprint, then:
    #   - add related records (tasks) to the resultset
    @api.model
    def _message_fetch(self, domain, *args, thread=None, **kwargs):
        base_res = super()._message_fetch(domain, *args, thread=thread, **kwargs)
        if thread == None or thread._name != "scrum.sprint":
            return base_res
        sprint_ids = thread.ids
        task_ids = (
            self.env["scrum.sprint.task"]
            .search([("sprint_id", "in", sprint_ids)])
            .mapped("task_id")
            .ids
        )
        tasks_domain = Domain.AND(
            [
                domain,
                [
                    ("res_id", "in", task_ids),
                    ("model", "=", "project.task"),
                    ("message_type", "!=", "user_notification"),
                ],
            ]
        )
        domain = Domain.AND([domain, tasks_domain])
        task_res = super()._message_fetch(domain, *args, thread=None, **kwargs)
        return {"messages": base_res["messages"] | task_res["messages"]}
