# -*- coding: utf-8 -*-
{
    'name': "Import Factors",

    # any module necessary for this one to work correctly
    'depends': ['base', 'base_import', 'mail', 'add_real_estate'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'wizards/download_template.xml',
        'wizards/import_template.xml',
        # 'views/temp.xml',
    ],


}
