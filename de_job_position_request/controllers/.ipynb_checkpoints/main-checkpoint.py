from odoo import http
from odoo.http import request
from datetime import datetime
from odoo.addons.website_sale.controllers.main import WebsiteSale


def leave_page_content():
    leave_type = request.env['hr.leave.type'].search([])
    employees = request.env['hr.employee'].search([])
    users = request.env['res.users'].search([])
    default_user_id = request.env.user.id
    print('user', request.env.user.id)
    login_user = request.env['res.users'].search([('id', '=', request.env.user.id)])
    email = login_user.login
    return {
        'leave_type': leave_type,
        'employees': employees,
        'users': users,
        'default_user_id': default_user_id,
        'email': email
    }


class MyLeaves(http.Controller):


    @http.route('/leave_page', type="http", auth="user", website=True)
    def leave_template(self, **kw):
        print("Execution Here.........................")
        return http.request.render('de_employee_leave_request.leave_template', leave_page_content())

    @http.route('/my_leave_page', type="http", auth="user", website=True)
    def leave_page_template(self, **kw):
        print("leave Execution Here.........................", request.env.user.name, request.env.user.id)
        leave_details = request.env['hr.leave'].sudo().search([('user_id', '=', request.env.user.id)])
        return request.render('de_employee_leave_request.leave_page_template', {'my_details': leave_details})

    @http.route('/create/leave', type="http", auth="public", website=True)
    def create_leave(self, **kw):
        print("Data Received.....", kw)
        fmt = '%Y-%m-%d'
        date_from = kw.get('request_date_from')
        date_to = kw.get('request_date_to')
        d1 = datetime.strptime(date_from, fmt)
        d2 = datetime.strptime(date_to, fmt)
        days_diff = float((d2 - d1).days)
        doctor_val = {
            'holiday_status_id': int(kw.get('holiday_status_id')),
            'employee_id': int(kw.get('employee_id')),
            'request_date_from': kw.get('request_date_from'),
            'request_date_to': kw.get('request_date_to'),
            'number_of_days': days_diff,
            'user_id': request.env.user.id,
            'name': kw.get('name'),
        }
        leave_record = request.env['hr.leave'].sudo().create(doctor_val)
        return request.render("de_employee_leave_request.patient_thanks", {})
