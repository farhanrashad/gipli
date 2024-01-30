# -*- coding: utf-8 -*-
###############################################################################
# This module has been developed by Dynexcel to enhance the functionality and user experience of the system. Dynexcel, with its commitment to excellence, ensures that this module adheres to the highest standards of quality and performance. We appreciate feedback and suggestions to continually improve our offerings. For any queries or support, please reach out to the Dynexcel team.
###############################################################################
{
    'name': "Student",
    'summary': """
    Student
        """,
    'description': """
        This module introduces the Student Portal, a centralized hub for all student-related records. Seamlessly access, manage, and track every student's academic journey, from enrollment to graduation, all in one place.
    """,
    'author': "Dynexcel",
    'website': "https://www.dynexcel.com",
    'category': 'CRM/School',
    'version': '16.0.0.2',
    'installable': True,
    'auto_install': False,
    'application': True,
    'license': 'OPL-1',
    'depends': [
        'de_school',
        'de_school_enrollment',
    ],
    'data': [
        'security/student_security.xml',
        # 'security/ir.model.access.csv',
        'views/school_student_menu.xml',
        'views/student_views.xml',
        'views/enrollment_views.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
}
