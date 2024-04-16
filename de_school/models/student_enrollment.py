# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import time
import logging

from psycopg2 import sql, DatabaseError

from odoo import api, fields, models, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from odoo.exceptions import ValidationError, UserError
from odoo.addons.base.models.res_partner import WARNING_MESSAGE, WARNING_HELP

class StudentEnrollment(models.Model):
    _name = 'oe.school.student.enrollment'
    _description = 'Student Enrollment'

    model = fields.Char('Related Document Model')
    res_id = fields.Many2oneReference('Related Document ID', model_field='model')
    school_name = fields.Char('School Name', required=True)
    school_year = fields.Char('School Year', required=True)
    level_grade = fields.Char('Grading Level', required=True)
    date_start = fields.Date('Start Date', required=True)
    date_end = fields.Date('End Date', required=True)
    address_school = fields.Char('School Address')