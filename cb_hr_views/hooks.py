# Copyright 2019 Creu Blanca
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
from psycopg2.extensions import AsIs
from odoo.tools import sql
from odoo import api, SUPERUSER_ID

_logger = logging.getLogger(__name__)


def pre_init_hook(cr):
    table = "hr_employee"
    column = "partner_id"
    field_type = "int4"
    if not sql.column_exists(cr, table, column):
        sql.create_column(cr, table, columnname=column, columntype=field_type)
    cr.execute(
        "SELECT id FROM %s WHERE %s is null", (AsIs(table), AsIs(column)))
    employee_ids = []
    for row in cr.fetchall():
        employee_ids.append(row[0])
    env = api.Environment(cr, SUPERUSER_ID, {})
    for employee in env['hr.employee'].browse(employee_ids):
        partner = env['res.partner'].create({
            'name': employee.name,
            'is_practitioner': True,
            'active': employee.active
        })
        cr.execute("UPDATE %s SET %s = %s WHERE id = %s", (
            AsIs(table), AsIs(column), partner.id, employee.id
        ))
    cr.execute(
        "SELECT id FROM %s WHERE %s is null", (AsIs(table), AsIs(column)))
