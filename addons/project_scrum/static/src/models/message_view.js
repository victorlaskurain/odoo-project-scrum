/** @odoo-module **/
/**
 * Copyright 2023 Victor Laskurain
 * License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
 */

import { registerPatch } from "@mail/model/model_core";

registerPatch({
    name: "MessageView",
    recordMethods: {
        async onClickTask(evt) {
            const ormService = this.env.services.orm;
            const actionService = this.env.services.action;
            const action = await ormService.call("project.task", "get_formview_action", [
                [this.message.task.id],
            ]);
            actionService.doAction(action);
        },
    },
});
