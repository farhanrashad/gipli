# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import timedelta, date
from odoo import api, fields, models, _
from odoo.tools import float_compare, format_datetime, format_time
from pytz import timezone, UTC


class CirculationAgreement(models.Model):
    _inherit = 'sale.order'

    is_borrow_order = fields.Boolean("Circulation Agreement")
    borrow_status = fields.Selection([
        ('draft', 'Draft'),
        ('submit','Pending Review'), #submitted and is awaiting review by the school or admission office.
        ('review','Under Review'), #reviewing the agreement and may request additional information or clarification.
        ('approved', 'Approved'), # reviewed and approved by the school, indicating that the student is accepted.
        ('pending', 'Pending Payment'), #accepted, and the agreement is pending payment of any fees or tuition.
        ('done', 'Done'), #The agreement is marked as done once the student has successfully 
        ('open', 'Running'), #The student is officially enrolled and attending classes.
        ('close', 'Close'), #close the contract, student completed the course.
        ('reject', 'Rejected'), #he school has reviewed the agreement and decided not to accept the student.
        ('cancel', 'Cancelled'), #student decides not to enroll after initially submitting the agreement,
        ('expire', 'Expired'), #Some enrollment agreements may have an expiration date, if that date passes without acceptance, the status could be "Expired.
    ], string="Status", default='draft', store=True, tracking=True, index=True,)