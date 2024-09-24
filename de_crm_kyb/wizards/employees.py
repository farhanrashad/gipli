# -*- coding: utf-8 -*-

from odoo import _, api, fields, models, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tools import format_date, frozendict


class Employee(models.TransientModel):
    _name = 'xpl.kyb.employees'
    _description = "Xpendless Employees"

    name = fields.Char(string='Employee')
    email = fields.Char(string='Email')
    mobile = fields.Char(string='Mobile')

    @api.model
    def default_get11111(self, fields):
        # Call super to get the default values
        res = super(Employee, self).default_get(fields)

        # Check if the current transient model has less than 10 records
        employees = self.search([])
        if len(employees) < 10:
            for i in range(1, 11):  # Create 10 records
                self.create({
                    'name': f'Employee {i}',  # Set a name or any other field
                })

        return res
    