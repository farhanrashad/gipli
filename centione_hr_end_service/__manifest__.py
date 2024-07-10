{
    'name': 'Centione Hr End Of Service',
    'data': [
        'security/ir.model.access.csv',
        'security/record_rule.xml',
        'wizard/end_of_service_incentive.xml',
        'views/turnover_reason.xml',
        # 'views/hr_resigned.xml',
        # 'views/hr_retired.xml',
        'views/hr_suspended.xml',
        'views/hr_termination.xml',
        'views/hr_employee.xml',
        'views/hr_config_settings.xml',
        'data/data.xml',
        'data/salary_rules.xml',
        'data/turn_over_reasons.xml',
    ],
    'author': 'Centione'
    , 'depends': ['hr',
                  'centione_hr_custody',
                  'hr_contract',
                  'centione_hr_payroll_base', 'address_hr_customs']
}
