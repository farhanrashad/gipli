# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.
{
    "name" : "Customer Vendor Field",
    "author" : "Softhealer Technologies",
    "website": "https://www.softhealer.com",
    "support": "support@softhealer.com",    
    "category": "Extra Tools",
    "summary": "This module provides two different boolean fields 1. Is Customer. 2. Is Vendor.",
    "description": """
        In the previous version of odoo, there is a boolean field in contacts for differentiating between customer and vendor but in odoo13 those fields are removed so it makes some difficulty for selecting customers and vendors. That's why we created this module it will help you to create customer and vendor separately as like create customer and vendor in the previous version of odoo. This module provides two different boolean fields 1. Is Customer. 2. Is Vendor. Now you can work with customers and vendors just like previous versions.
customer field
customer option
vendor filed
is customer field
is customer option
supplier field
is supplied field
supplier options
customer vendor field odoo
customer supplier field odoo

                    """,    
    "version":"13.0.1",
    "depends" : [
                "base",
                "sale_management",
                "purchase",
        ],
    
    "data" : [
           "views/partner_view.xml",
           "views/sale_view.xml",
           "views/purchase_view.xml"
            ],            
           
    "images": ["static/description/background.png",],        
    "auto_install":False,
    "application" : True,
    "installable" : True,
    "post_init_hook": "post_init_hook",
    "currency": "EUR",
    "price": 15
    
}
