from odoo import api, fields, models
from datetime import datetime
from dateutil import relativedelta

class Contract(models.Model):
    _inherit='hr.contract'

    employee_percentage = fields.Float(string="Employee Percentage",related='job_id.employee_percentage',store=True)
    medical_package = fields.Float(string="Medical Package",related='employee_id.medical_package',store=True)
    hr_responsible_ids = fields.Many2many(comodel_name="res.users", relation="cont_res_users", string="HR Responsible")




    def job_family_alert(self):
        for contract in  self.env['hr.contract'].sudo().search([('state', '=', 'open')]):
            if contract.date_end and contract.job_id:
                if contract.job_id.job_family_id:
                    months = relativedelta.relativedelta(datetime.now().date(), contract.date_end).months
                    if months == contract.job_id.job_family_id.alert:
                        if contract.employee_id.parent_id:
                            note="""هذا العقد سوف ينتهي بعد {months} شهور""".format(months=contract.job_id.job_family_id.alert)
                            self.send_email_for_user(contract.employee_id.work_email,note)
                            for other in contract.job_id.job_family_id.other_employees:
                                self.send_email_for_user(other.work_email,note)



    def send_email_for_user(self, email, note):
        mail_content = note
        main_content = {
            'subject': note,
            'author_id': self.env.user.partner_id.id,
            'body_html': mail_content,
            'email_to': email,
            'state': "outgoing",

        }
        res = self.env['mail.mail'].sudo().create(main_content).send()

