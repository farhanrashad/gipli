# -*- coding: utf-8 -*-
# Part of Softhealer Technologies.

from . import models

# TODO: Apply proper fix & remove in master
def post_init_hook(cr, registry):
    # Update old customers and vendors.
    query = "UPDATE res_partner SET is_customer='t' where customer_rank > 0; UPDATE res_partner SET is_supplier='t' where supplier_rank > 0;"
    cr.execute(query)            
