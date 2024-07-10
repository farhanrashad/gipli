from odoo import models, fields, api, _


class MissedDocument(models.Model):
    _name = 'missed.document'

    name = fields.Char('Name',required=True)

