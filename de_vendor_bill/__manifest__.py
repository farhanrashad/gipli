# -*- coding: utf-8 -*-
#################################################################################
# Author      : Dynexcel (<https://dynexcel.com/>)
# Copyright(c): 2015-Present dynexcel.com
# All Rights Reserved.
#
#
#
# This program is copyright property of the author mentioned above.
# You can`t redistribute it and/or modify it.
#
#
# You should have received a copy of the License along with this program.
#################################################################################
{
  "name"                 :  "Vendor Bill Approval",
  "summary"              :  "This Module add the approval of vendor bill functionality in vendor bills",
  "category"             :  "Accounting",
  "version"              :  "13.0.0.5",
  "sequence"             :  1,
  "author"               :  "Dynexcel",
  "license"              :  "AGPL-3",
  "website"              :  "http://dynexcel.com",
  "description"          :  """

""",
  "live_test_url"        :  "",
  "depends"              :  [
                             'account',
                            ],
    "data":  [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/vendor_bill_approval_view.xml',
        'views/vendor_bill_state_view.xml',
        'views/vendor_bill_view.xml'
        ],
  "images"               :  ['static/description/Banner.png'],
  "application"          :  True,
  "installable"          :  True,
  "auto_install"         :  False,
  "price"                :  0,
  "currency"             :  "EUR",
  "images"		 :['static/description/banner.jpg'],
}