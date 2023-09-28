from odoo import models, fields, api

class LeaveEncashWizard(models.TransientModel):
    _name = 'hr.leave.encash.wizard'
    _description = 'Leave Encash Wizard'

    # Define fields for any parameters you want to pass to the report
    date_start = fields.Date(string='Start Date', required=True)
    date_end = fields.Date(string='End Date', required=True)
    report_filter = fields.Selection(
        [('by_employee', 'By Employee'), ('by_leave_type', 'By Leave Type')],
        string='Report Filter',
        default='by_employee', required=True,
    )


    # Define a method to generate the report
    def generate_report(self):
        # Get list of unique Employees
        employee_list = []
        total_employees = 0
        query = """
            select distinct l.employee_id, e.name
            from hr_leave_encash l
            join hr_employee e on l.employee_id = e.id
            where e.active = True
            and l.date between %(date_start)s and %(date_end)s
        """
        args = {
            'date_start': self.date_start,
            'date_end': self.date_end,
        }
        self.env.cr.execute(query, args)
        rs_employees = self._cr.dictfetchall()
        for emp in rs_employees:
            vals = {
                'employee_id': emp['employee_id'],
                'employee_name': emp['name'],
            }
            employee_list.append(vals)
            total_employees += 1

        # Get list of unique Leave Type
        leave_type_list = []
        query = """
            select distinct l.holiday_status_id, t.name
            from hr_leave_encash l
            join hr_leave_type t on l.holiday_status_id = t.id
            where l.date between %(date_start)s and %(date_end)s
        """
        args = {
            'date_start': self.date_start,
            'date_end': self.date_end,
        }
        self.env.cr.execute(query, args)
        rs_leave_types = self._cr.dictfetchall()
        for lt in rs_leave_types:
            vals = {
                'leave_type_id': lt['holiday_status_id'],
                'leave_type_name': lt['name'],
            }
            leave_type_list.append(vals)


        
        domain = []
        if self.date_start:
            domain += [('date','>=',self.date_start)]
        if self.date_end:
            domain += [('date','<=',self.date_end)]
        hr_leave_encash_ids = self.env['hr.leave.encash'].search(domain)
        leave_encash_list = []
        for record in hr_leave_encash_ids:
            vals = {
                'name': record.name,
                'holiday_status_name': record.holiday_status_id.name,
                'holiday_status_id': record.holiday_status_id.id,
                'employee_name': record.employee_id.name,
                'employee_id': record.employee_id.id,
                'number_of_leaves': record.number_of_days if record.leave_type_request_unit == 'days' else record.number_of_hours,
                'leave_type_request_unit': record.leave_type_request_unit,
                'amount_total': record.amount_total,
                'currency_id': record.currency_id,
                'state':record.state,
            }
            leave_encash_list.append(vals)
        # Get the report action
        report_action = self.env.ref('de_hr_leave_encashment.action_report_leave_encash').report_action(self)

        
        # Set the context for the report (pass any parameters)
        report_action.update({'data': {
            'date_start': self.date_start,
            'date_end': self.date_end,
            'form_data': self.read()[0],
            'leave_encash_ids': leave_encash_list,
            'employees': employee_list,
            'leave_types': leave_type_list,
            'report_filter': self.report_filter,
            'total_employees': total_employees,
            'amount_total': sum(hr_leave_encash_ids.mapped('amount_total'))
        }})

        return report_action
