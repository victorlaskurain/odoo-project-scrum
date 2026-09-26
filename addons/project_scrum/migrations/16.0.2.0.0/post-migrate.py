# Copyright 2026 Victor Laskurain
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).


def migrate(cr, version):
    # drops the function, aggregate and the view because of "CASCADE"
    cr.execute(
        """
DROP FUNCTION IF EXISTS COALESCE_AGG_sfunc(state ANYELEMENT, value ANYELEMENT) CASCADE;
"""
    )
