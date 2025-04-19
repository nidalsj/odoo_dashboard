from odoo import fields, models, api


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    total_sales_card_color = fields.Char('Total Sales Card Color')
    total_purchases_card_color = fields.Char('Total Purchases Card Color')
    total_customers_card_color = fields.Char('Total Customers Card Color')
    sales_today_card_color = fields.Char('Sales Today Card Color')
    total_sales_text_color = fields.Char('Total Sales Text Color')
    total_purchases_text_color = fields.Char('Total Purchases Text Color')
    total_customers_text_color = fields.Char('Total Customers Text Color')
    sales_today_text_color = fields.Char('Sales Today Text Color')
    delivery_chart_color = fields.Char('Delivery Chart Color')
    sale_orders_chart_color = fields.Char('Sale Order Chart Color')
    top_products_chart_color = fields.Char('Top Products Chart Color')
    top_customers_chart_color = fields.Char('Top Customers Chart Color')

    def set_values(self):
        super(ResConfigSettings, self).set_values()
        params = self.env['ir.config_parameter'].sudo()
        color_fields = [
            'total_sales_card_color', 'total_purchases_card_color', 'total_customers_card_color', 'sales_today_card_color',
            'total_sales_text_color', 'total_purchases_text_color', 'total_customers_text_color', 'sales_today_text_color',
            'delivery_chart_color', 'sale_orders_chart_color', 'top_products_chart_color', 'top_customers_chart_color'
        ]
        for field in color_fields:
            params.set_param(f'dashboard_settings.{field}', getattr(self, field) or '')

    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        params = self.env['ir.config_parameter'].sudo()
        color_fields = [
            'total_sales_card_color', 'total_purchases_card_color', 'total_customers_card_color', 'sales_today_card_color',
            'total_sales_text_color', 'total_purchases_text_color', 'total_customers_text_color', 'sales_today_text_color',
            'delivery_chart_color', 'sale_orders_chart_color', 'top_products_chart_color', 'top_customers_chart_color'
        ]
        for field in color_fields:
            res[field] = params.get_param(f'dashboard_settings.{field}', default='')
        return res