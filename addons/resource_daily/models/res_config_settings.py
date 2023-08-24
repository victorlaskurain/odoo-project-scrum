# Copyright 2023 Victor Laskurain
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _

EARLIEST_DATE_DEFAULT = "2000-01-01"
LATEST_DATE_DEFAULT = "2050-12-31"


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    # The fields must be datetime because res.config.settings does not
    # support date fields. This can produce timezone related date
    # displacements (you ask for earliest_date = 2000-01-01 but get
    # 1999-12-31 for example). In this context we can ignore these
    # displacements: just be generous with the supported date range.
    earliest_date = fields.Datetime(
        "Earliest Date",
        default=EARLIEST_DATE_DEFAULT,
        help="Earliest date for resource availability computations",
        config_parameter="resource_daily.earliest_date",
    )

    latest_date = fields.Datetime(
        "Latest Date",
        default=LATEST_DATE_DEFAULT,
        help="Latest date for resource availability computations",
        config_parameter="resource_daily.latest_date",
    )
