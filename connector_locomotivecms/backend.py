# -*- coding: utf-8 -*-
# Copyright 2017 Akretion (http://www.akretion.com).
# @author Sébastien BEAU <sebastien.beau@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).


from odoo.addons.connector.backend import Backend


locomotive = Backend('locomotive')
""" LocomotiveCMS Backend"""

locomotive_v3 = Backend(parent=locomotive, version='locomotive_v3')
""" LocomotiveCMS Backend"""
