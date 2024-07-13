
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import logging

LOGGER = logging.getLogger(__name__)

class hrattendancezkinherit(models.Model):
    _inherit = 'hr.attendance.zk.temp'


    def make_logged(self):
        for rec in self:
            rec.logged = True


    def make_logged_false(self):
        for rec in self:
            rec.logged = False