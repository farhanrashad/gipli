# -*- coding: utf-8 -*-

from odoo import models, fields, api


class hr_employee_inherit(models.Model):
    _inherit = 'hr.employee'

    employee_arabic_name = fields.Char('Employee Arabic Name')
    old_code = fields.Char('Old Code')
    old_code_1 = fields.Char('Old Code 1')
    phone_num = fields.Char('Phone')
    franchise = fields.Many2one('franchise.type', string='Franchise')
    hire_date = fields.Date('Hire Date')
    transfer_date = fields.Date('Transfer Date')
    egy_bank_account = fields.Char('Egy Bank Account')
    cib_bank_account = fields.Char('CIB Bank Account')
    hiring_source = fields.Char('Hiring source')
    resignation_date = fields.Date('Resignation date')
    bank_application = fields.Boolean('Bank Application')
    bank_application_date = fields.Date('Bank Application Date')

    national_id = fields.Boolean('National ID')
    national_id_file = fields.Binary('National ID')
    national_id_file_name = fields.Char('National ID')

    graduation_cert = fields.Boolean('Graduation Certificate')
    graduation_cert_file = fields.Binary('Graduation Certificate')
    graduation_cert_file_name = fields.Char('Graduation Certificate')

    birth_cert = fields.Boolean('Birth Certificate')
    birth_cert_file = fields.Binary('Birth Certificate')
    birth_cert_file_name = fields.Char('Birth Certificate')

    criminal_records_cert = fields.Boolean('Criminal Records Certificate')
    criminal_records_cert_file = fields.Binary('Criminal Records Certificate')
    criminal_records_cert_file_name = fields.Char('Criminal Records Certificate')

    work_stub = fields.Boolean('كعب عمل')
    work_stub_file = fields.Binary('كعب عمل')
    work_stub_file_name = fields.Char('كعب عمل')

    six_photos = fields.Boolean('Six Photos')
    six_photos_file = fields.Binary('Six Photos')
    six_photos_file_name = fields.Char('Six Photos')

    insurance_form = fields.Boolean('Insurance Form')
    insurance_form_file= fields.Binary('Insurance Form')
    insurance_form_file_name= fields.Char('Insurance Form')

    cv_form = fields.Boolean('CV')
    cv_form_file = fields.Binary('CV')
    cv_form_file_name = fields.Char('CV')

    army_cert = fields.Boolean('Army Certificate')
    army_cert_file = fields.Binary('Army Certificate')
    army_cert_file_name = fields.Char('Army Certificate')

    @api.onchange('national_id_file',
                  'graduation_cert_file','birth_cert_file',
                  'criminal_records_cert_file','work_stub_file',
                  'six_photos_file','insurance_form_file',
                  'cv_form_file','army_cert_file')
    def onchange_all_files(self):
        self.national_id = True if self.national_id_file else False
        self.graduation_cert = True if self.graduation_cert_file else False
        self.birth_cert = True if self.birth_cert_file else False
        self.criminal_records_cert = True if self.criminal_records_cert_file else False
        self.work_stub = True if self.work_stub_file else False
        self.six_photos= True if self.six_photos_file else False
        self.insurance_form = True if self.insurance_form_file else False
        self.cv_form = True if self.cv_form_file else False
        self.army_cert = True if self.army_cert_file else False


    completed_docs = fields.Boolean('Completed',compute='_calc_completed_docs',store=True)
    not_completed_docs = fields.Boolean('Not Completed',compute='_calc_completed_docs',store=True)
    docs_progress = fields.Float(string="Progress",compute='_calc_completed_docs',store=True)

    @api.depends('national_id',
                  'graduation_cert','birth_cert',
                  'criminal_records_cert','work_stub',
                  'six_photos','insurance_form',
                  'cv_form','army_cert')
    def _calc_completed_docs(self):
       for rec in self:
           if rec.national_id and \
               rec.graduation_cert and \
               rec.birth_cert and rec.criminal_records_cert and \
               rec.work_stub and rec.six_photos and \
               rec.insurance_form and rec.cv_form and rec.army_cert:
               rec.completed_docs=True
               rec.not_completed_docs=False
           else:
               rec.completed_docs = False
               rec.not_completed_docs = True

           pref=[rec.national_id,
               rec.graduation_cert ,
               rec.birth_cert , rec.criminal_records_cert ,
               rec.work_stub , rec.six_photos ,
               rec.insurance_form , rec.cv_form , rec.army_cert]
           try:
               rec.docs_progress=(pref.count(True)/len(pref))*100

           except:
               rec.docs_progress =0
