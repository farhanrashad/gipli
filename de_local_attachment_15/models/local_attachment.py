import base64
from odoo import models, fields, api
import os


import logging
_logger = logging.getLogger(__name__)
class Attachment(models.Model):
    _inherit = 'ir.attachment'


    @api.model
    def create(self, values):
        # Save the attachment to the local folder
        datass = None
        if values.get('raw'):
            datass = values['raw']
        attachment = super(Attachment, self).create(values)
        try:
            if datass and attachment.create_uid and attachment.create_uid.display_name != 'OdooBot':
                raw_attachment = attachment.datas
                attachment.datas = None
                data = base64.b64decode(raw_attachment)
                folder_path = self.env['ir.config_parameter'].sudo().get_param('de_local_attachment.attachment_folder')
                if folder_path:
                    with open(folder_path + str(attachment.id), 'wb') as f:
                        f.write(data)   
        except Exception as excp:
            _logger.exception(excp)
        return attachment


    def unlink(self):
        folder_path = self.env['ir.config_parameter'].sudo().get_param('de_local_attachment.attachment_folder')
        if folder_path:
            for attachment in self:
                path = folder_path + str(attachment.id)
                if os.path.exists(path):
                    os.remove(path)
        return super(Attachment, self).unlink()


# @api.model
# def _get_file(self, record):
#     # open the file in binary mode
#     with open(record.name, 'rb') as file:
#         # read the file content and create an attachment download record
#         data = file.read()
#         download_record = self.env['attachment.download'].create({
#             'name': record.name,
#             'file': data
#         })
#         return download_record.id


# class AttachmentDownload(models.Model):
#     _name = 'attachment.download'
#     _description = 'Attachment Download Record'

#     name = fields.Char(string='Name', required=True)
#     file = fields.Binary(string='File', required=True)
    
# def unlink(self):
#     result = super(Attachment, self).unlink()
#     return result



# to download and preview 
# attachment = self.env['ir.attachment'].browse(attachment_id)
# with open(local_folder + '/' + attachment.name, 'rb') as f:
# attachment_data = f.read()
# return attachment_data


# 'E:\path\path_of_given_file'
# folder_path = os.path.join(os.path.expanduser('~'), record.folder)
# if not os.path.exists(folder_path):
#     os.makedirs(folder_path)
# file_path = os.path.join(folder_path, record.filename)
# with open(file_path, 'wb') as f:
#     f.write(record.attachment.decode('base64'))