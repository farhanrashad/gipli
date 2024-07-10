{
    'name': 'Capital Organization Chart',
    'version': '1.0',
    'category': 'Human Resource',
    'summary': 'Capital Organization Chart',
    'description': """
Capital Organization Chart:
=======================================================

* To be listed
    """,
    'author': 'Centione',
    'website': 'https://www.centione.com',
    'depends': [ 'hr'],
    'data': [

          'views/template.xml',
          'views/views.xml',
    ],
    'qweb': [
        'static/src/xml/capital_templates.xml',

    ],
    'installable': True,
    'auto_install': False,
}
