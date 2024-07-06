# Copyright 2024 Victor Laskurain
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from datetime import datetime

from odoo.tests import tagged, TransactionCase


@tagged("post_install", "-at_install")
class TestOneWeek(TransactionCase):
    def compare_to_baseline(self, compute_leaves):
        DailyCalendar = self.env["resource.daily.calendar"]
        calendars = self.env["resource.calendar"].search([])
        ranges = [
            (datetime(2024, 5, 5), datetime(2024, 4, 10)),  # empty range
            (datetime(2024, 1, 1), datetime(2024, 1, 5)),  # some random range
            (datetime(2024, 5, 5), datetime(2024, 6, 10)),  # some random range
            (datetime(2024, 1, 1), datetime(2025, 1, 1)),  # full year
        ]
        for calendar in calendars:
            daily_calendar = DailyCalendar.search([("calendar_id", "=", calendar.id)])
            self.assertTrue(daily_calendar.exists())
            for begin, end in ranges:
                baseline = calendar.get_work_duration_data(begin, end, compute_leaves)
                value = daily_calendar.get_work_duration_data(
                    begin, end, compute_leaves
                )
                # turn 189.99999999999991 hours into 190.00,
                # 259.94/259.92 days into 259.9, etc.
                baseline["hours"] = round(baseline["hours"], 2)
                baseline["days"] = round(baseline["days"], 1)
                value["hours"] = round(value["hours"], 2)
                value["days"] = round(value["days"], 1)
                msg = 'Testing calendar "%s" with range [%s, %s)' % (
                    calendar.name,
                    begin,
                    end,
                )
                self.assertEqual(baseline, value, msg)

    def test_no_leaves(self):
        self.compare_to_baseline(True)
        self.compare_to_baseline(False)

    def test_leaves(self):
        Leave = self.env["resource.calendar.leaves"]
        new_year = Leave.create(
            {
                "name": "New year",
                "date_from": datetime(2024, 1, 1),
                "date_to": datetime(2024, 1, 2),
            }
        )
        x_mas = Leave.create(
            {
                "name": "Xmas",
                "date_from": datetime(2024, 12, 25),
                "date_to": datetime(2024, 12, 26),
            }
        )
        x_mas_eve_afternoon = Leave.create(
            {
                "name": "Xmas Eve",
                "date_from": datetime(2024, 12, 24, 15, 0, 0),
                "date_to": datetime(2024, 12, 26),
            }
        )
        self.compare_to_baseline(True)
        self.compare_to_baseline(False)

    def test_leaves_single_calendar(self):
        std_calendar = self.env.ref("resource.resource_calendar_std")
        Leave = self.env["resource.calendar.leaves"]
        new_year = Leave.create(
            {
                "name": "New year",
                "date_from": datetime(2024, 1, 1),
                "date_to": datetime(2024, 1, 2),
                "calendar_id": std_calendar.id,
            }
        )
        x_mas = Leave.create(
            {
                "name": "Xmas",
                "date_from": datetime(2024, 12, 25),
                "date_to": datetime(2024, 12, 26),
                "calendar_id": std_calendar.id,
            }
        )
        x_mas_eve_afternoon = Leave.create(
            {
                "name": "Xmas Eve",
                "date_from": datetime(2024, 12, 24, 15, 0, 0),
                "date_to": datetime(2024, 12, 26),
                "calendar_id": std_calendar.id,
            }
        )
        self.compare_to_baseline(True)
        self.compare_to_baseline(False)
