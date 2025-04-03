from odoo import models, fields, api, _
from odoo.tools import date_utils
from datetime import date, datetime, timedelta


class DashboardHandler(models.Model):
    _name = "dashboard.handler"
    _description = "Prepare Data for Dashboard"