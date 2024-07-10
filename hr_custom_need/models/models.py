# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError


class Position(models.Model):
    _inherit = 'hr.job'

    job_code_id = fields.Many2one(comodel_name="job.code", string="Job Code", required=False, )
    cluster_id = fields.Many2one(comodel_name="hr.cluster", string="Cluster", required=False, related='job_code_id.cluster_id',store=True )
    payscal_id = fields.Many2one(comodel_name="pay.scal", string="PayScal")
    payscal_attribute = fields.Char(string="PayScal Attribute")
    grade = fields.Char(string="Grade", compute='_calc_grade',store=True)

    @api.depends('job_code_id.numeric_grade', 'payscal_attribute')
    def _calc_grade(self):
        for rec in self:
            st=""
            if rec.job_code_id.numeric_grade:
                st+=rec.job_code_id.numeric_grade
            if rec.payscal_attribute:
                st += rec.payscal_attribute
            rec.grade =st


class Clusters(models.Model):
    _name = 'hr.cluster'

    name = fields.Char(string="Name", required=False, )
    prefix = fields.Integer(string="Prefix", required=False, )


class JobCode(models.Model):
    _name = 'job.code'

    name = fields.Char(string="Name", required=False, )
    numeric_grade = fields.Char(string="Numeric Grade", required=False, )
    cluster_id = fields.Many2one(comodel_name="hr.cluster", string="Cluster", required=False, )



class PayScal(models.Model):
    _name = 'pay.scal'

    name = fields.Char(string="Name", required=False, )
    min = fields.Integer(string="Min", required=False, )
    max = fields.Integer(string="Max", required=False, )


class Contract(models.Model):
    _inherit = 'hr.contract'


    @api.constrains('job_id','wage','state')
    def check_job_payscal_id(self):
        for contract in self:
            if contract.job_id.payscal_id and contract.state not in ['cancel','close']:
                if contract.wage not in range(contract.job_id.payscal_id.min,contract.job_id.payscal_id.max):
                    raise ValidationError("Wage Not In Range min:"+str(contract.job_id.payscal_id.min)+",max:"+str(contract.job_id.payscal_id.max))
class Employee(models.Model):
    _inherit = 'hr.employee'
    certificate = fields.Selection([
         ('undergrade', 'Undergrade'),
        ('graduate', 'Graduate'),
        ('bachelor', 'Bachelor'),
        ('master', 'Master'),
        ('doctor', 'Doctor'),
        ('other', 'Other'),
    ], 'Certificate Level', default='other', groups="hr.group_hr_user", tracking=True)
#
#     military_status = fields.Selection(
#         [('not_req', 'Not Required'), ('post', 'Postponed'),
#          ('complete', 'complete'), ('exemption', 'Exemption'),
#          ('current', 'Currently serving ')], string="Military Status")

