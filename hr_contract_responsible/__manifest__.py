# -*- coding: utf-8 -*-
{
    'name': "hr_contract_responsible",

    # any module necessary for this one to work correctly
    'depends': ['base','hr', 'hr_contract'],

    # always loaded
    'data': [
        'security/ir.model.access.csv',
        'security/rule.xml',
        'views/social_insurance.xml',
        'views/medical_insurance.xml',
        'views/job.xml',
        'views/contract.xml',
        'views/medical_history.xml',
        'views/menus.xml',
    ],

}
