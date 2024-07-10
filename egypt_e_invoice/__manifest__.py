# -*- coding: utf-8 -*-

{
    "name": "Egyptian Electronic Invoice",
    "version": "14",
    "author": "Ideal Solutions - Saad El Wardany",
    "category": "Accounting",
    "depends": ["account","uom"],
    "data": [
        "security/security.xml",
        "security/ir.model.access.csv",
        "data/einvoice.uom.csv",
        "data/einvoice.activity.type.csv",
        "data/einvoice.tax.type.csv",
        "data/einvoice.tax.subtype.csv",
        "views/invoice.xml",
        "views/views.xml",
        "views/res_config.xml",
    ],
    "installable": True,
    "auto_install": False,
    "pre_init_hook": "pre_init_hook",
}
