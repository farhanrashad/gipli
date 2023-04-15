from odoo import http
from odoo.addons.web.controllers.main import Binary
from odoo.http import request
import os
import base64

import logging
_logger = logging.getLogger(__name__)
class AttachmentControllerInherit(Binary):

    @http.route([
        '/web/content/<string:model>/<int:id>/<string:field>',
        '/web/content/<string:model>/<int:id>/<string:field>/<string:filename>'], type='http', auth="public")
    def content_common(self, xmlid=None, model='ir.attachment', id=None, field='raw',
                       filename=None, filename_field='name', unique=None, mimetype=None,
                       download=None, data=None, token=None, access_token=None, **kw):
        
        res = super(AttachmentControllerInherit, self).content_common(xmlid=None, model='ir.attachment', id=None, field='raw',
                       filename=None, filename_field='name', unique=None, mimetype=None,
                       download=None, data=None, token=None, access_token=None, **kw)
        try:
            attachment  = request.env['ir.attachment'].search([('id','=',id)])
            folder_path = request.env['ir.config_parameter'].sudo().get_param('de_local_attachment.attachment_folder')
            # path = folder_path + str(attachment.res_id)
            path = folder_path + str(attachment.id)
            file_content = None
            with open(path, 'rb') as file:
            # read the file content
                file_content = file.read()
            # encode the file content
            encoded_content = base64.b64encode(file_content)

            # check if the attachment exists
            if attachment:
                # get the file content
                file_content = file_content
                # file_content = attachment.datas
                # get the file name
                file_name = attachment.name
                # get the file mime type
                file_mimetype = attachment.mimetype
                # create the http response object
                response = request.make_response(file_content,
                                            [('Content-Type', file_mimetype),
                                            ('Content-Disposition', 'attachment; filename=%s' % file_name)])
                # return the response
                return response
            else:
                # if the attachment does not exist, return an error message
                return "Attachment not found"
        except Exception as excp:
            _logger.exception(excp)

    # @http.route([
    #     '/web/content/<string:model>/<int:id>/<string:field>',
    #     '/web/content/<string:model>/<int:id>/<string:field>/<string:filename>'], type='http', auth="public")
    # def content_common(self, xmlid=None, model='ir.attachment', id=None, field='datas',
    #                    filename=None, filename_field='name', unique=None, mimetype=None,
    #                    download=None, data=None, token=None, access_token=None, **kw):
        
    #     res = super(AttachmentControllerInherit, self).content_common(xmlid=None, model='ir.attachment', id=None, field='datas',
    #                    filename=None, filename_field='name', unique=None, mimetype=None,
    #                    download=None, data=None, token=None, access_token=None, **kw)
    #     try:
    #         attachment  = request.env['ir.attachment'].search([('id','=',id)])
    #         folder_path = request.env['ir.config_parameter'].sudo().get_param('de_local_attachment.attachment_folder')
    #         # path = folder_path + str(attachment.res_id)
    #         path = folder_path + str(attachment.id)
    #         file_content = None
    #         with open(path, 'rb') as file:
    #         # read the file content
    #             file_content = file.read()
    #         # encode the file content
    #         encoded_content = base64.b64encode(file_content)

    #         # check if the attachment exists
    #         if attachment:
    #             # get the file content
    #             file_content = file_content
    #             # file_content = attachment.datas
    #             # get the file name
    #             file_name = attachment.name
    #             # get the file mime type
    #             file_mimetype = attachment.mimetype
    #             # create the http response object
    #             response = request.make_response(file_content,
    #                                         [('Content-Type', file_mimetype),
    #                                         ('Content-Disposition', 'attachment; filename=%s' % file_name)])
    #             # return the response
    #             return response
    #         else:
    #             # if the attachment does not exist, return an error message
    #             return "Attachment not found"
    #     except Exception as excp:
    #         _logger.exception(excp)







