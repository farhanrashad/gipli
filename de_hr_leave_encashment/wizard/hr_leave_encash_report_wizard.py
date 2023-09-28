from odoo import models, fields, api

class LeaveEncashWizard(models.TransientModel):
    _name = 'hr.leave.encash.wizard'
    _description = 'Leave Encash Wizard'

    # Define fields for any parameters you want to pass to the report
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')

    # Define a method to generate the report
    def generate_report(self):
        # Get the report action
        report_action = self.env.ref('de_hr_leave_encashment.leave_encash_details_report').report_action(self)

        # Set the context for the report (pass any parameters)
        report_action.update({'data': {
            'start_date': self.start_date,
            'end_date': self.end_date,
        }})

        return report_action
