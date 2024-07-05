# -*- coding: utf-8 -*-

from . import controllers
from . import models


def uninstall_hook(env):
    companies = env["res.company"].search([])
    hostel_locations = companies.mapped("hostel_location_id")
    hostel_locations.active = False
    companies.write({"hostel_location_id": False})
