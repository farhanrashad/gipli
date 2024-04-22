# -*- coding: utf-8 -*-
# Part of Dynexcel. See LICENSE file for full copyright and licensing details.
{
    'name': "Partner Survey",

    'summary': """
    Partner Survey
        """,
    'description': """
        Partner Survey:-
        Create multiple survey forms for partner interviews
    """,
    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",
    'category': 'Marketing',
    'version': '14.0.0.1',

    'depends': ['base', 'survey', 'contacts'],
    "price": 75,
    "currency": "USD",
    'data': [
        'security/ir.model.access.csv',
        'views/res_partner_views.xml',
        'views/partner_category_views.xml',
        'views/partner_survey_views.xml',
    ],
    "auto_install": False,
    "installable": True,
    "live_test_url":'https://www.youtube.com/watch?v=2A6UAiSnpW0',
    "images":['static/description/banner.jpg'],
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: