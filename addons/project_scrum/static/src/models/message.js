/** @odoo-module **/
/**
 * Copyright 2023 Victor Laskurain
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
 */

import { registerModel, registerPatch } from "@mail/model/model_core";
import { attr, one } from "@mail/model/model_field";

function isDataForSprintChatbox(data) {
    return data.model == "project.task" && data.sprint_id;
}

registerModel({
    name: "Task",
    fields: {
        name: attr(),
        id: attr({
            identifying: true,
        }),
    },
});

registerPatch({
    name: "Message",
    fields: { task: one("Task") },
    modelMethods: {
        convertData(data) {
            let data2;
            if (isDataForSprintChatbox(data)) {
                // hack data so that it hangs from the chatbox of the
                // sprint even though is linked to a task.
                data.model = "scrum.sprint";
                data.res_id = data.sprint_id;
                data2 = this._super(data);
                data2.task = data.task;
            } else {
                data2 = this._super(data);
            }
            return data2;
        },
    },
});
