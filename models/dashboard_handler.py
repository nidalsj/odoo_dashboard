from odoo import models, fields, api, _
from odoo.tools import date_utils
from datetime import date, datetime, timedelta
from odoo.tools import format_amount
from odoo.http import request


class DashboardHandler(models.Model):
    _name = "dashboard.handler"
    _description = "Prepare Data for Dashboard"

    # Function to pass active session info without inheriting ir.http model
    def get_active_session_info(self):
        user = request.env.user.name

        return {
            'user': user,
        }

    def get_dashboard_kpi_card_data(self):
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
        total_customers_domain = [('customer_rank', '>', 0)]
        total_customers = self.env['res.partner'].search_count(total_customers_domain)

        # Sales Orders Today
        sale_orders_today = self.env['sale.order'].search_count([
            ('state', '=', 'sale'),
            ('date_order', '>=', today_start),
            ('date_order', '<=', today_end),
        ])

        sales_today_domain = [
            ['create_date', '>=', today_start],
            ['create_date', '<=', today_end],
            ['state', '=', 'sale']
        ]

        return {
            'total_sales': formatted_sales,
            'total_purchases': formatted_purchases,
            'total_customers': total_customers,
            'sales_orders_today': sale_orders_today,
            'sales_today_domain': sales_today_domain,
        }
    
    def get_deliveries_today_chart_data(self, target_date=None):
        """Returns a grouped count of deliveries by status for today"""
        target_date = target_date or date.today().strftime('%Y-%m-%d')
        status_mapping = dict(self.env["stock.picking"]._fields["state"].selection)

        query = """
            SELECT COUNT(*) AS count, state FROM stock_picking
            WHERE DATE(date) = %s
            GROUP BY state
        """
        self.env.cr.execute(query, (target_date,))
        result = self.env.cr.dictfetchall()

        data = {
            status_mapping.get(item["state"], item["state"]): item["count"]
            for item in result
        }

        return {
            'labels': list(data.keys()),
            'values': list(data.values())
        }

    def get_monthly_sales_chart_data(self, target_date=None):
        """Sale orders per month for current year"""
        current_date = datetime.strptime(target_date, '%Y-%m-%d') if target_date else date.today()
        start_date = date(current_date.year, 1, 1)
        end_date = date(current_date.year, 12, 31)

        query = """
            SELECT COUNT(*) AS total_orders, 
                TO_CHAR(create_date, 'Month') AS order_month
            FROM sale_order
            WHERE create_date BETWEEN %s AND %s
            AND state = 'sale'
            GROUP BY order_month
            ORDER BY MIN(create_date);
        """
        self.env.cr.execute(query, (start_date, end_date))
        result = self.env.cr.dictfetchall()

        labels = [row['order_month'].strip() for row in result]  # strip spaces from Month names
        values = [row['total_orders'] for row in result]

        return {'labels': labels, 'values': values}
    
    def get_top_products_chart_data(self, target_date=None):
        """Returns top 20 products by number of confirmed sale orders"""
        current_date = datetime.strptime(target_date, '%Y-%m-%d') if target_date else date.today()
        start_date = date(current_date.year, 1, 1)
        end_date = date(current_date.year, 12, 31)

        query = """
            SELECT pt.name AS product_name, COUNT(so.id) AS sale_count
            FROM sale_order_line sol
            JOIN sale_order so ON sol.order_id = so.id
            JOIN product_product pp ON sol.product_id = pp.id
            JOIN product_template pt ON pp.product_tmpl_id = pt.id
            WHERE so.state = 'sale'
            AND so.create_date BETWEEN %s AND %s
            GROUP BY pt.name
            ORDER BY sale_count DESC
            LIMIT 20
        """
        self.env.cr.execute(query, (start_date, end_date))
        result = self.env.cr.dictfetchall()
        user_lang = self.env.user.lang or 'en_US'

        labels = [row['product_name'].get(user_lang, '') for row in result]
        values = [row['sale_count'] for row in result]

        return {'labels': labels, 'values': values}
    
    def get_top_customers_chart_data(self, target_date=None, limit=20):
        """Returns top 20 customers and their total confirmed sales in the current year"""
        current_date = datetime.strptime(target_date, '%Y-%m-%d') if target_date else date.today()
        start_date = date(current_date.year, 1, 1)
        end_date = date(current_date.year, 12, 31)

        user_lang = self.env.user.lang or 'en_US'
        user_currency = self.env.user.company_id.currency_id

        query = """
            SELECT rp.name AS customer_name, SUM(so.amount_total) AS total_sales
            FROM sale_order so
            JOIN res_partner rp ON so.partner_id = rp.id
            WHERE so.state = 'sale'
            AND so.date_order BETWEEN %s AND %s
            GROUP BY rp.name
            ORDER BY total_sales DESC
            LIMIT %s
        """
        self.env.cr.execute(query, (start_date, end_date, limit))
        result = self.env.cr.dictfetchall()

        labels = [row['customer_name'] for row in result]
        raw_values = [round(row['total_sales'], 2) for row in result]

        return {'labels': labels, 'values': raw_values}
    
    def get_employees_with_birthdays_this_month(self):
        """Employees whose birthdays are between today and the end of this month"""
        today = date.today()
        current_month = today.strftime('%m')
        current_day = today.strftime('%d')

        query = """
            SELECT id, name AS display_name, birthday
            FROM hr_employee
            WHERE birthday IS NOT NULL
            AND TO_CHAR(birthday, 'MM') = %s
            AND TO_CHAR(birthday, 'DD') >= %s
            ORDER BY TO_CHAR(birthday, 'MM-DD')
        """
        self.env.cr.execute(query, (current_month, current_day))
        result = self.env.cr.dictfetchall()

        for row in result:
            if row['birthday']:
                row['birthday'] = row['birthday'].strftime('%b %d, %Y')

        return result
    
    def get_invoice_payment_summary(self):
        query = """
            SELECT
                COALESCE(SUM(amount_total), 0.0) AS total_invoiced,
                COALESCE(SUM(amount_total - amount_residual), 0.0) AS total_paid,
                COALESCE(SUM(amount_residual), 0.0) AS total_pending
            FROM account_move
            WHERE move_type = 'out_invoice' AND state = 'posted';
        """
        self.env.cr.execute(query)
        result = self.env.cr.dictfetchone()
        currency = self.env.company.currency_id.symbol

        format_result = {
            "total_invoiced": f"{currency} {result['total_invoiced']:.2f}",
            "total_paid": f"{currency} {result['total_paid']:.2f}",
            "total_pending": f"{currency} {result['total_pending']:.2f}",
        }

        return format_result
    
    def get_dashboard_chart_loader_data(self, target_date=None):
        """Preparing Data for all four charts"""
        target_date = target_date or date.today().strftime('%Y-%m-%d')
        chart_loader_data = {}

        delivery_status_count = self.get_deliveries_today_chart_data(target_date)
        chart_loader_data['delivery_labels'] = delivery_status_count['labels']
        chart_loader_data['delivery_values'] = delivery_status_count['values']

        sale_order_count = self.get_monthly_sales_chart_data(target_date)
        chart_loader_data['order_labels'] = sale_order_count['labels']
        chart_loader_data['order_values'] = sale_order_count['values']

        top_products_count = self.get_top_products_chart_data(target_date)
        chart_loader_data['products_labels'] = top_products_count['labels']
        chart_loader_data['products_values'] = top_products_count['values']

        top_customers_amounts = self.get_top_customers_chart_data(target_date)
        chart_loader_data['customers_labels'] = top_customers_amounts['labels']
        chart_loader_data['customers_values'] = top_customers_amounts['values']

        chart_loader_data['employee_birthdays'] = self.get_employees_with_birthdays_this_month()

        payments_summary_data = self.get_invoice_payment_summary()
        chart_loader_data['payments_summary'] = payments_summary_data

        return chart_loader_data
    