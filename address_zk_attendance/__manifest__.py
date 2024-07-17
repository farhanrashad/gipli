# -*- coding: utf-8 -*-
{
    'name': "Address zk Attendance Module",

    'summary': """
        Integration module for zk attendance machines
        """,

    'description': """
        Make sure the following python packages are installed:
        xmltodict
        pytz
        python-dateutil
        
        A text file for processing attendance logs should be placed in the following path:
        /opt/odoo/pharos/custom/zkLogs.txt
    """,

    'author': "Centione",
    'website': "http://www.centione.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/11.0/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','hr','hr_attendance'],

    # always loaded
    'data': [
        'views/sequence.xml',
        'views/views.xml',
        'security/ir.model.access.csv',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}