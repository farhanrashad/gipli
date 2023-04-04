# -*- coding: utf-8 -*-
{
    "name": "Clickup Connector",
    "category": 'Integration',
    "summary": 'Clickup-Odoo Integration',
    "description": """
	 
   
    """,
    "sequence": 1,
    "author": "Dynexcel",
    "website": "http://www.dynexcel.co",
    "version": '13.1.0.0',
    "depends": ['project','web','portal'],
    "data": [
        'security/ir.model.access.csv',
        'data/data.xml',
        'data/res_partner_clickup.xml',
        'views/clickup_config_view.xml',
        'views/clickup_folder_view.xml',
        'views/clickup_lists_view.xml',
        'views/clickup_webhook_view.xml',
        'views/project_task_view.xml',
        'views/project_tags_view.xml',
        'views/ir_attachment_view.xml',
#         'views/res_config_view.xml',
        'views/clickup_menu.xml',
    ],
    
    "price": 25,
    "currency": 'EUR',
    "installable": True,
    "application": True,
    "auto_install": False,
}
