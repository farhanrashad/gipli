# -- coding: utf-8 --
{
    'name': "Sale Invoice report",

    'summary': """
        A report for sale invoice""",

    'description': """
        Long description of module's purpose
    """,

    'author': "Dynexcel",
    'website': "http://www.dynexcel.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/13.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base','account'],

    # always loaded
    'data': [
     'report/sale_invoice_report.xml',
     'report/sale_invoice_report_tem.xml'
    ],
    # only loaded in demonstration mode
    'application':True,
    'installation':True,
    'auto_install':False,
}