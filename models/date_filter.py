from odoo import models, fields, api, _
from odoo.tools import date_utils
from datetime import date, datetime


class DashboardDateFilters(models.Model):
    _name = 'dashboard.date.filter'
    _description = 'Dashboard Date Filter'

    filter_name = fields.Char(string='Filter Name')
    filter_days = fields.Integer(string='Days Count')