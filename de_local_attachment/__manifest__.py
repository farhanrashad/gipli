# -*- coding: utf-8 -*-
{
    'name': "Attachment Managment on Local",

    'summary': """
        Attachment Managment on Local
        1- Define your path for local storage in config parameters(local attachment folder) like D:/attachments/
        2- Now when any attachment in your system is uploaded will be saved into this local folder not on db
        3- When you delete this attachment then attachment will be deleted from local as well as records meta from system
        4- When you download the attachment attachment will be downloaded from the local disk.
        """,

    'description': """
        Attachment Managment on Local 
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # for the full list
    # 'category': '',
    'version': '0.0.0.1',

    # any module necessary for this one to work correctly
    'depends': [],

    # always loaded
    'data': [
        'views/res_config_settings_views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}
