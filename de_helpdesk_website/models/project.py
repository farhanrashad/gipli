# -*- coding: utf-8 -*-

import base64

from odoo import api, Command, fields, models, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from odoo.addons.http_routing.models.ir_http import slug


class Project(models.Model):
    _inherit = 'project.project'

    is_published = fields.Boolean("Web Published", store=True, )

    website_id = fields.Many2one('website', domain="[('company_id', '=?', company_id)]", compute='_compute_website_id', store=True, readonly=False)
    website_url = fields.Char('Url', store=True,
                              compute='_compute_website_url',)

    #@api.depends('module_helpdesk_website')
    def _compute_is_published(self):
        for record in self:
            record.is_published = record.module_helpdesk_website
            
    @api.depends('company_id')
    def _compute_website_id(self):
        for record in self:
            record.website_id = record.company_id.website_id


    @api.depends('is_published')
    def _compute_website_url(self):
        for record in self:
            if record.id:  # Check if the record has an ID
                record.website_url = "/support/%s" % slug(record)
            else:
                record.website_url = False
            
    def open_website_url(self):
        #self._get_project_by_website_url('/support/support-desk-5')
        return self.env['website'].get_client_action(self.website_url, website_id=self.website_id.id)

    def _get_project_by_website_url(self, url):
        #raise UserError(url)
        project = self.env["project.project"].search([
            ('website_url', '=', url)
        ], limit=10)
        return project


    def create(self, vals):
        project = super(Project, self).create(vals)
        project._manage_website_menu()
        return project

    def write(self, vals):
        res = super(Project, self).write(vals)
        self._manage_website_menu()
        self._enable_published()
        return res

    
    def _manage_website_menu(self):
        for project in self:
            parent_menu = project.website_id.menu_id
            existing_menu = self.env['website.menu'].search([('url', '=', project.website_url)], limit=1)
            if project.is_published:
                if not existing_menu:
                    self.env['website.menu'].sudo().create({
                        'name': project.name,
                        'url': project.website_url,
                        'parent_id': parent_menu.id,
                        'sequence': 50,
                        'website_id': project.website_id.id,
                    })
            else:
                if existing_menu:
                    existing_menu.unlink()
            #raise UserError('hello')

    def _enable_published(self):
        for project in self:
            if project.is_published != project.module_helpdesk_website:
                project.write({'is_published': project.module_helpdesk_website})
    
    def _create_ticket(self, vals):
        # Create a new task
        task_vals = {
            'name': vals.get('name'),
            'email_cc': vals.get('email_from'),
            #'contact_name': vals.get('contact_name'),
            'description': vals.get('description'),
            'project_id': vals.get('project_id'),
            'partner_id': vals.get('partner_id'),
            'is_ticket': True,
        }
        task = self.env['project.task'].sudo().create(task_vals)

        # Handle attachments and create a message
        attachment_files = vals.get('attachment_files', [])

        attachment_ids = []
    
        if attachment_files:
            for attachment in attachment_files:
                attached_file = attachment.read()
                if attached_file:  # Ensure the attachment is not empty
                    attachment_id = self.env['ir.attachment'].sudo().create({
                        'name': attachment.filename,
                        'res_model': 'project.task',
                        'res_id': task.id,
                        'type': 'binary',
                        'datas': base64.b64encode(attached_file).decode('ascii'),
                    })
                    attachment_ids.append(attachment_id.id)

        # Create a message with attachments
        # Create a message with attachments
        body = """
            Dear {contact_name}, <br/><br/>
            Your request {name} has been received and is being reviewed by our {team} team. <br/><br/>
            The reference for your ticket is {ticket_no}. <br/><br/>
            To provide any additional information, simply reply to this email.
            """.format(
                contact_name=vals.get('contact_name'),
                name=vals.get('name'),
                ticket_no=task.ticket_no,
                team=task.project_id.name,
            )

        self.env['mail.message'].create({
            'message_type': 'auto_comment',
            'subtype_id': self.env.ref('mail.mt_note').id,
            'subject': vals.get('name'),
            'body': body,
            'model': 'project.task',
            'res_id': task.id,
            'attachment_ids': [(6, 0, attachment_ids)],
        })
        return task