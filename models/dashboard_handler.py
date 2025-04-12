from odoo import models, fields, api, _
from odoo.tools import date_utils
from datetime import date, datetime, timedelta
from odoo.tools import format_amount


class DashboardHandler(models.Model):
    _name = "dashboard.handler"
    _description = "Prepare Data for Dashboard"

    def get_kpi_card_data(self):
        currency = self.env.company.currency_id
        currency_symbol = currency.symbol
        today_start = datetime.combine(fields.Date.today(), datetime.min.time())
        today_end = datetime.combine(fields.Date.today(), datetime.max.time())

        # Total Sales
        sales_order_domain = [('state', '=', 'sale')]
        sales_orders = self.env['sale.order'].search(sales_order_domain)
        total_sales = sum(s.amount_total for s in sales_orders)
        formatted_sales = format_amount(self.env, total_sales, currency)

        # Total Purchases
        purchase_orders_domain = [('state', '=', 'purchase')]
        purchase_orders = self.env['purchase.order'].search(purchase_orders_domain)
        total_purchases = sum(p.amount_total for p in purchase_orders)
        formatted_purchases = format_amount(self.env, total_purchases, currency)

        # Total Customers
        total_customers_domain = []
        total_customers = self.env['res.partner'].search_count(total_customers_domain)

        # Sales Orders Today
        sale_orders_today = self.env['sale.order'].search_count([
            ('state', '=', 'sale'),
            ('date_order', '>=', today_start),
            ('date_order', '<=', today_end),
        ])

        return {
            'total_sales': formatted_sales,
            'total_purchases': formatted_purchases,
            'total_customers': total_customers,
            'sales_orders_today': sale_orders_today,
        }