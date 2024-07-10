# -*- coding: utf-8 -*-
from odoo import http , fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo.http import request
import json
import logging

LOGGER = logging.getLogger(__name__)

class OrganizationChart(http.Controller):

    @http.route(['/page/organization_chart'], auth='user', website=True,type='http', csrf=True)
    def get_org_chart_all(self, **post):

        data = request.env['hr.employee'].get_organization_chart()
        result_dumps = json.dumps(data)
        data_str =  "var d = " + result_dumps
        return request.render('address_hr_organization_chart.org_chart_template', {'data':data_str,'department':'Capital Organization Chart'})

    @http.route(['/page/organization-chart/<int:emp_id>'], auth='user', website=True, type='http', csrf=True)
    def get_org_chart_emp(self,emp_id, **post):
        employee = request.env['hr.employee'].browse(emp_id)
        data = employee.get_organization_chart(employee)
        result_dumps = json.dumps(data)
        data_str = "var d = " + result_dumps
        return request.render('address_hr_organization_chart.org_chart_template', {'data': data_str,'department':employee.department_id.name or 'Capital Organization Chart'})


