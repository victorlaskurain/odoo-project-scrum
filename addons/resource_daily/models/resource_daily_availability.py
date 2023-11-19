# Copyright 2023 Victor Laskurain
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import models, fields, api, _

from .res_config_settings import EARLIEST_DATE_DEFAULT, LATEST_DATE_DEFAULT


class ResourceDailyAvailability(models.Model):
    _name = "resource.daily.availability"
    _order = "calendar_id, date DESC"
    _description = "Resource availability expanded to every day."
    _auto = False
    _log_access = False

    calendar_id = fields.Many2one("resource.calendar", readonly=True)
    resource_id = fields.Many2one("resource.resource", readonly=True)
    date = fields.Date("Date", readonly=True)
    attendance_range = fields.Char("Attendance Ranges", readonly=True)
    leave_range = fields.Char("Leave Ranges", readonly=True)
    availability_range = fields.Char("Availability Ranges", readonly=True)
    availability_hours = fields.Float("Availability Hours", readonly=True)

    def init(self):
        self.env.cr.execute(
            """
DROP FUNCTION IF EXISTS RESOURCE_DAILY_GET_ODOO_WEEK_TYPE(day DATE) CASCADE;
CREATE FUNCTION RESOURCE_DAILY_GET_ODOO_WEEK_TYPE(day DATE) RETURNS VARCHAR AS
$$
SELECT CAST(CAST(FLOOR((day - '0001-01-01'::date) / 7) AS INTEGER) %% 2 AS VARCHAR);
$$ LANGUAGE SQL IMMUTABLE;

-- this view needs to be refreshed when the series boundaries change. Holds a record
-- for each calendar day supported in the following queries.
DROP MATERIALIZED VIEW IF EXISTS resource_daily_every_day;
CREATE MATERIALIZED VIEW resource_daily_every_day AS (
    -- dates is a virtual table that either holds the earliest and
    -- latest values set in the configuration or the default values.
    WITH dates AS (
        SELECT DATE(COALESCE(icp1.value, %(EARLIEST_DATE_DEFAULT)s)) AS earliest,
               DATE(COALESCE(icp2.value, %(LATEST_DATE_DEFAULT)s)) AS latest
        FROM (SELECT 1) AS placeholder
        LEFT JOIN ir_config_parameter AS icp1
               ON icp1.key = 'resource_daily.earliest_date'
        LEFT JOIN ir_config_parameter AS icp2
               ON icp2.key = 'resource_daily.latest_date'
    )
    SELECT day::date AS date,
        CAST(EXTRACT(isodow FROM day::date) - 1 AS VARCHAR) AS day_of_week
        FROM dates
        CROSS JOIN GENERATE_SERIES(
            dates.earliest,
            dates.latest,
            '1 DAY'
        ) AS day
);
CREATE UNIQUE INDEX resource_daily_every_day_unique_idx ON resource_daily_every_day (date);

DROP FUNCTION IF EXISTS RESOURCE_DAILY_TSRANGE CASCADE;
CREATE FUNCTION RESOURCE_DAILY_TSRANGE(
    a TIMESTAMP WITHOUT TIME ZONE,
    b TIMESTAMP WITHOUT TIME ZONE
) RETURNS TSRANGE AS
$$
    SELECT CASE
        WHEN a IS NULL AND b IS NULL THEN
            TSRANGE('2000-01-01', '2000-01-01') -- empty range
        ELSE
            TSRANGE(a, b)
        END;
$$ LANGUAGE SQL IMMUTABLE;

-- resource.calendar.attendance data expanded to each supporte day and
-- exposed as TSMULTIRANGE-s (UTC).
--
-- materializing this view would be the most efficient implementation
-- but but updating the every_day_attendance_range can be expensive
-- and we would have to refresh this view each time every_day changes
-- but also each time the calendar's attendances are modified. Even
-- though attendance edition is not a common operation penalizing it
-- for a possibly premature optimization does not seem justified.
DROP VIEW IF EXISTS resource_daily_attendance;
CREATE VIEW resource_daily_attendance AS (
    SELECT rc.id * 100000000
               + EXTRACT(YEAR  FROM ed.date) * 10000
               + EXTRACT(MONTH FROM ed.date) *   100
               + EXTRACT(DAY   FROM ed.date) *     1 AS id,
           rc.id AS calendar_id,
           ed.date AS date,
           RANGE_AGG(
               RESOURCE_DAILY_TSRANGE(
                   (
                       ed.date + MAKE_INTERVAL(
                           MINS => CAST(rca.hour_from * 60 AS INTEGER)
                       )
                   ) AT TIME ZONE rc.tz AT TIME ZONE 'UTC',
                   (
                       ed.date + MAKE_INTERVAL(
                           MINS => CAST(rca.hour_to * 60 AS INTEGER)
                       )
                   ) AT TIME ZONE rc.tz AT TIME ZONE 'UTC'
               )
           ) AS attendance_range
    FROM       resource_daily_every_day AS ed
    CROSS JOIN resource_calendar AS rc
    LEFT  JOIN resource_calendar_attendance AS rca
            ON rca.calendar_id = rc.id  AND ed.day_of_week = rca.dayofweek
               AND CASE rc.two_weeks_calendar
                       WHEN TRUE THEN
                           ed.day_of_week = rca.dayofweek
                           AND RESOURCE_DAILY_GET_ODOO_WEEK_TYPE(ed.date) = rca.week_type
                       ELSE
                           TRUE
                   END
               AND (rca.date_from IS NULL OR rca.date_from < ed.date)
               AND (rca.date_to   IS NULL OR ed.date       < rca.date_to)
    WHERE rca.display_type IS NULL
    GROUP BY rc.id, ed.date
);

DROP FUNCTION IF EXISTS RESOURCE_DAILY_TSMULTIRANGE_TOTAL CASCADE;
CREATE FUNCTION RESOURCE_DAILY_TSMULTIRANGE_TOTAL(
    mr TSMULTIRANGE
) RETURNS INTERVAL AS
$$
DECLARE
    r TSRANGE;
    acc INTERVAL;
BEGIN
    acc := 0;
    FOR r IN SELECT UNNEST(mr)
    LOOP
        acc := acc + (UPPER(r) - LOWER(r));
    END LOOP;
    RETURN acc;
END;
$$ LANGUAGE PLPGSQL IMMUTABLE;

DROP VIEW IF EXISTS resource_daily_availability;
CREATE VIEW resource_daily_availability AS (
    SELECT rda.id * 10000 + COALESCE(rr.id, 0) AS id,
           rda.date AS date,
           rda.calendar_id AS calendar_id,
           rr.id AS resource_id,
           RANGE_AGG(rda.attendance_range) AS attendance_range,
           RANGE_AGG(
               RESOURCE_DAILY_TSRANGE(grcl.date_from, grcl.date_to)
           ) AS leave_range,
           RANGE_AGG(rda.attendance_range)
           - RANGE_AGG(
               RESOURCE_DAILY_TSRANGE(grcl.date_from, grcl.date_to)
           ) AS availability_range,
           EXTRACT(EPOCH FROM
               RESOURCE_DAILY_TSMULTIRANGE_TOTAL(
                   RANGE_AGG(rda.attendance_range)
                   - RANGE_AGG(
                       RESOURCE_DAILY_TSRANGE(grcl.date_from, grcl.date_to)
                   )
               )
           ) / 60.0 / 60.0 AS availability_hours
    FROM       resource_daily_attendance AS rda
    -- In order to represent global leaves with rows whose resource is
    -- NULL add a NULL row as required to the resouce table.
    INNER JOIN (
        SELECT id, calendar_id FROM resource_resource
        UNION
        SELECT NULL, NULL
    ) AS rr
            ON rr.calendar_id = rda.calendar_id OR rr.id IS NULL
    LEFT  JOIN resource_calendar_leaves AS grcl
            ON grcl.calendar_id = rda.calendar_id
               AND (grcl.resource_id IS NULL OR grcl.resource_id = rr.id)
               AND rda.date BETWEEN grcl.date_from::date AND grcl.date_to::date
    GROUP BY rda.id, rda.date, rda.calendar_id, rr.id
);
""",
            globals(),
        )
