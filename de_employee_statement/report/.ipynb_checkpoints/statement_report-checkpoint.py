# -*- coding: utf-8 -*-
from odoo import models, fields
from odoo.exceptions import UserError
from datetime import datetime
from datetime import date, timedelta
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from dateutil.relativedelta import relativedelta
import datetime
import pytz
import calendar


class EmployeeStatementXlS(models.AbstractModel):
    _name = 'report.de_employee_statement.hr_employee_statement_report_xlsx'
    _description = 'Employee Statment XLsx report'
    _inherit = 'report.report_xlsx.abstract'
    
  
    def generate_xlsx_report(self, workbook, data, lines):
        data = self.env['employee.statement.wizard'].browse(self.env.context.get('active_ids'))