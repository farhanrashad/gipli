# -*- coding: utf-8 -*-
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import json
import logging

LOGGER = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    sub_employee_ids = fields.One2many(comodel_name="hr.employee", inverse_name="coach_id", string="", required=False, )

    # @api.constrains('coach_id')
    # def _check_coach(self):
    #     if self.coach_id and self.coach_id.department_id != self.department_id:
    #         raise ValidationError("Manager Must Be in the same department of the employee")

    @api.constrains('parent_id')
    def _check_hierarchy(self):
        if not self._check_recursion():
            raise models.ValidationError(
                'Error! You cannot create recursive categories.')


    def find_childern(self, parent, lis):
        print("D>>D",parent)
        if parent.child_ids or parent.sub_employee_ids:
            index = 0
            sub_emp = parent.sub_employee_ids.filtered(lambda x: x.department_id == parent.department_id)
            child_emps = parent.child_ids | sub_emp
            for child in child_emps:
            # for child in parent.child_ids:
                lis.append({
                    'image': "<img src=/web/image?model=hr.employee&id=" + str(child.id) +"&field=image_small />",
                    'name': child.name,
                     'title': child.job_id.name or '',
                     'children': []
                })
                self.find_childern(child, lis[index]['children'])
                index += 1
        else:
            return False

    @api.model
    def get_organization_chart(self,employee=None):
        index = 0
        if not employee:
            result = {
                'image': "<img style=\"max-width:70px;\" src=/web/image?model=res.company&id=" + str(
                    self.env.user.company_id.id) + "&field=logo />",
                'name': 'Capital',
                'title': 'Capital',
                'children': [],
            }
            emp_parents = self.search([('parent_id','=',False)])
            for emp in emp_parents:
                if emp.id==44326:
                    pass
                print(">>S>S",emp)
                result['children'].append(
                    {'image': "<img src=/web/image?model=hr.employee&id=" + str(emp.id) + "&field=image_small />",
                     'name': emp.name,
                     'title': emp.job_id.name or '',
                     'children': [], })
                self.find_childern(emp, result['children'][index]['children'])

                index += 1

        else:
            result = {}
            employee_node = {
                    'image': "<img src=/web/image?model=hr.employee&id=" + str(employee.id) + "&field=image_small />",
                    'name': employee.name,
                    'title': employee.job_id.name or '',
                    'children': []
                }
            self.find_childern(employee, employee_node['children'])
            if employee.parent_id:
                head_node = {
                    'image': "<img src=/web/image?model=hr.employee&id=" + str(employee.parent_id.id) + "&field=image_small />",
                    'name': employee.parent_id.name,
                    'title': employee.parent_id.job_id.name or '',
                    'children': []
                }
                if employee.coach_id:
                    manager_node = {
                        'image': "<img src=/web/image?model=hr.employee&id=" + str(employee.coach_id.id) + "&field=image_small />",
                        'name': employee.coach_id.name,
                        'title': employee.coach_id.job_id.name or '',
                        'children': []
                    }
                    manager_node['children'].append(employee_node)
                    head_node['children'].append(manager_node)

                else:
                    head_node['children'].append(employee_node)

                result = head_node
            elif employee.coach_id:
                manager_node = {
                    'image': "<img src=/web/image?model=hr.employee&id=" + str(
                        employee.coach_id.id) + "&field=image_small />",
                    'name': employee.coach_id.name,
                    'title': employee.coach_id.job_id.name or '',
                    'children': []
                }
                manager_node['children'].append(employee_node)

                result = manager_node

            else:
                # result= {
                #     'image': "<img src=/web/image?model=hr.employee&id=" + str(employee.id) + "&field=image_small />",
                #      'name': employee.name,
                #      'title': employee.job_id.name or '',
                #      'children':[]
                #      }
                result = employee_node

        return result

    def get_org_chart(self):
        return {
            'type': 'ir.actions.act_url',
            'name': self.department_id.name or '',
            'target': 'new',
            'url': "/page/organization-chart/%s" % (self.id,)
        }


