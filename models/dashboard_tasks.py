from odoo import fields, models


class DashboardTasks(models.Model):
    _name = 'dashboard.tasks'
    _description = 'Dashboard Tasks'

    name = fields.Char(string='Task')
    completed = fields.Boolean()
