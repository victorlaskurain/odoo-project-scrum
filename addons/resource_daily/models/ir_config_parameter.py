# Copyright 2023 Victor Laskurain
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models


class IrConfigParameter(models.Model):
    _inherit = "ir.config_parameter"

    # if the user changes both parameters at the same this
    # implementation will refresh the view twice. Given that this
    # particular refresh is almost instantaneos we opt to bear with
    # this and keep the implementation trivial
    def set_param(self, key, value):
        """Refresh view on parameter changes"""
        res = super().set_param(key, value)
        if key in ("resource_daily.earliest_date", "resource_daily.latest_date"):
            self.env.flush_all()  # without this the REFRESH might not see the change.
            self.env.cr.execute("REFRESH MATERIALIZED VIEW resource_daily_every_day;")
        return res
