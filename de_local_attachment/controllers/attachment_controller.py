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
    def content_common(self, xmlid=None, model='ir.attachment', id=None, field='datas',
                       filename=None, filename_field='name', unique=None, mimetype=None,
                       download=None, data=None, token=None, access_token=None, **kw):
        
        res = super(AttachmentControllerInherit, self).content_common(xmlid=None, model='ir.attachment', id=None, field='datas',
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



    # @http.route('/attachment/download/<int:download_id>', type='http', auth='public')
    # def content(self, download_id, **kw):
    #     # fetch the attachment download record
    #     download_record = http.request.env['attachment.download'].browse(download_id)

    #     record = download_record
    #     download_record.unlink()
    #     # return the file content and set the content type to octet-stream
    #     return http.request.make_response(download_record.file, [('Content-Type', 'octet-stream'), ('Content-Disposition', 'attachment; filename="{}"'.format(download_record.name))])


    # status, headers, content = request.env['ir.http'].binary_content(
    #     xmlid=xmlid, model=model, id=id, field=field, unique=unique, filename=filename,
    #     filename_field=filename_field, download=download, mimetype=mimetype, access_token=access_token)













        # if status != 200:
        #     return request.env['ir.http']._response_by_status(status, headers, content)
        # else:
        #     content_base64 = base64.b64decode(content)
        #     headers.append(('Content-Length', len(content_base64)))
        #     response = request.make_response(content_base64, headers)
        # if token:
        #     response.set_cookie('fileToken', token)


        
    
        # return response