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


    @api.model
    def get_dashboard_kpi_card_data(self, **kwargs):
        """Returns data for all 4 KPI cards based on the selected period"""
        currency = self.env.company.currency_id
        date_from, date_to = kwargs.get('date_from'), kwargs.get('date_to')

        date_domain = []
        if date_from:
            date_domain += [('date_order', '>=', date_from)]
        if date_to:
            date_domain += [('date_order', '<=', date_to)]

        # Sales
        sales_domain = [('state','=','sale')] + date_domain
        sales_orders = self.env['sale.order'].search(sales_domain)
        total_sales = format_amount(self.env, sum(sales_orders.mapped('amount_total')), currency)

        # Purchases
        purchase_domain = [('state','=','purchase')] + date_domain
        purchase_orders = self.env['purchase.order'].search(purchase_domain)
        total_purchases = format_amount(self.env, sum(purchase_orders.mapped('amount_total')), currency)

        # Customers
        customer_ids = sales_orders.mapped('partner_id').ids
        customers_domain = [('id','in',customer_ids)]
        total_customers = len(set(customer_ids))

        # Sales today
        today_start = datetime.combine(fields.Date.today(), datetime.min.time())
        today_end = datetime.combine(fields.Date.today(), datetime.max.time())
        sales_today_domain = [
            ('state','=','sale'),
            ('date_order','>=',fields.Datetime.to_string(today_start)),
            ('date_order','<=',fields.Datetime.to_string(today_end)),
        ]
        sales_orders_today = self.env['sale.order'].search_count(sales_today_domain)

        return {
            'total_sales': total_sales,
            'total_purchases': total_purchases,
            'total_customers': total_customers,
            'sales_orders_today': sales_orders_today,
            'sales_domain': sales_domain,
            'purchase_domain': purchase_domain,
            'customers_domain': customers_domain,
            'sales_today_domain': sales_today_domain,
        }
    

    def get_deliveries_today_chart_data(self):
        """Returns a grouped count of deliveries by status for CURRENT DAY ONLY!"""
        date_today = date.today().strftime('%Y-%m-%d')
        status_mapping = dict(self.env["stock.picking"]._fields["state"].selection)

        query = """
            SELECT COUNT(*) AS count, state FROM stock_picking
            WHERE DATE(scheduled_date) = %s
            GROUP BY state
        """
        self.env.cr.execute(query, (date_today,))
        result = self.env.cr.dictfetchall()

        data = {
            status_mapping.get(item["state"], item["state"]): item["count"]
            for item in result
        }

        date_today = fields.Date.from_string(date_today)
        day_start = datetime.combine(date_today,datetime.min.time())
        day_end = datetime.combine(date_today,datetime.max.time())

        domain = [
            ('scheduled_date', '>=', fields.Datetime.to_string(day_start)),
            ('scheduled_date', '<=', fields.Datetime.to_string(day_end)),
        ]

        return {
            'labels': list(data.keys()),
            'values': list(data.values()),
            'domain': domain
        }


    def get_monthly_sales_chart_data(self):
        """Returns confirmed sale orders grouped by month for CURRENT YEAR ONLY!"""
        date_today = date.today()

        orders = self.env['sale.order'].search([
            ('create_date', '>=', date(date_today.year, 1, 1)),
            ('create_date', '<=', date(date_today.year, 12, 31)),
            ('state', '=', 'sale')
        ])

        data = {}

        for order in orders:
            month_number = order.create_date.month
            month_name = order.create_date.strftime("%B")

            if month_number not in data:
                data[month_number] = {"month": month_name,"count": 0,"ids": []}

            data[month_number]["count"] += 1
            data[month_number]["ids"].append(order.id)

        data = dict(sorted(data.items()))

        return {
            'labels': [x["month"] for x in data.values()],
            'values': [x["count"] for x in data.values()],
            'record_ids': {x["month"]: x["ids"] for x in data.values()}
        }
    

    @api.model
    def get_top_products_chart_data(self, **kwargs):
        """Returns top 10 products based on quantity sold in the selected period"""
        date_from = kwargs.get('date_from')
        date_to = kwargs.get('date_to')
        domain = [('order_id.state','=','sale')]

        if date_from:
            domain.append(('order_id.create_date','>=',date_from))

        if date_to:
            domain.append(('order_id.create_date','<=',date_to))

        lines = self.env['sale.order.line'].search(domain)
        products = {}

        for line in lines:

            if line.product_id.id not in products:
                products[line.product_id.id] = {
                    'name': line.product_id.display_name,
                    'amount': 0,
                    'order_ids': []
                }

            products[line.product_id.id]['amount'] += line.price_subtotal
            products[line.product_id.id]['order_ids'].append(line.order_id.id)

        products = sorted(products.values(),key=lambda x: x['amount'],reverse=True)[:10]

        return {
            'labels': [p['name'] for p in products],
            'values': [p['amount'] for p in products],
            'record_ids': {p['name']: list(set(p['order_ids']))for p in products}
        }
    

    @api.model
    def get_top_customers_chart_data(self, **kwargs):
        """Returns top 5 customers based on total amount spent in the selected period"""
        date_from = kwargs.get('date_from')
        date_to = kwargs.get('date_to')
        domain = [('state','=','sale')]

        if date_from:
            domain.append(('date_order','>=',date_from))

        if date_to:
            domain.append(('date_order','<=',date_to))

        orders = self.env['sale.order'].search(domain)
        customers = {}

        for order in orders:
            customer = order.partner_id
            if customer.id not in customers:
                customers[customer.id] = {
                    'name': customer.display_name,
                    'amount': 0,
                    'order_ids': []
                }

            customers[customer.id]['amount'] += order.amount_total
            customers[customer.id]['order_ids'].append(order.id)

        customers = sorted(customers.values(),key=lambda x: x['amount'],reverse=True)[:5]

        return {
            'labels': [c['name'] for c in customers],
            'values': [c['amount'] for c in customers],
            'record_ids': {c['name']: list(set(c['order_ids']))for c in customers}
        }
    

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
    

    def get_invoice_payment_summary(self, date_from=None, date_to=None):
        date_domain = ""
        params = []

        if date_from:
            date_domain += " AND invoice_date >= %s"
            params.append(date_from)

        if date_to:
            date_domain += " AND invoice_date <= %s"
            params.append(date_to)

        query = f"""
            SELECT
                COALESCE(SUM(amount_total), 0.0) AS total_invoiced,
                COALESCE(SUM(amount_total - amount_residual), 0.0) AS total_paid,
                COALESCE(SUM(amount_residual), 0.0) AS total_pending
            FROM account_move
            WHERE move_type = 'out_invoice'
            AND state = 'posted'
            {date_domain}
        """

        self.env.cr.execute(query, params)
        result = self.env.cr.dictfetchone()
        currency = self.env.company.currency_id.symbol

        return {
            "total_invoiced": f"{currency} {result['total_invoiced']:.2f}",
            "total_paid": f"{currency} {result['total_paid']:.2f}",
            "total_pending": f"{currency} {result['total_pending']:.2f}",
        }
    

    @api.model
    def get_dashboard_chart_loader_data(self, **kwargs):
        """Fetching data for all charts and tables in one go to minimize RPC calls. Date filters are applied where needed"""
        date_from = kwargs.get('date_from')
        date_to = kwargs.get('date_to')
        chart_loader_data = {}

        delivery_status_count = self.get_deliveries_today_chart_data()
        chart_loader_data['delivery_labels'] = delivery_status_count['labels']
        chart_loader_data['delivery_values'] = delivery_status_count['values']
        chart_loader_data['delivery_domain'] = delivery_status_count['domain']

        sale_order_count = self.get_monthly_sales_chart_data()
        chart_loader_data['order_labels'] = sale_order_count['labels']
        chart_loader_data['order_values'] = sale_order_count['values']
        chart_loader_data['order_record_ids'] = sale_order_count['record_ids']

        top_products_count = self.get_top_products_chart_data(date_from=date_from, date_to=date_to)
        chart_loader_data['products_labels'] = top_products_count['labels']
        chart_loader_data['products_values'] = top_products_count['values']
        chart_loader_data['products_record_ids'] = top_products_count['record_ids']

        top_customers_amounts = self.get_top_customers_chart_data(date_from=date_from, date_to=date_to)
        chart_loader_data['customers_labels'] = top_customers_amounts['labels']
        chart_loader_data['customers_values'] = top_customers_amounts['values']
        chart_loader_data['customers_record_ids'] = top_customers_amounts['record_ids']

        chart_loader_data['employee_birthdays'] = self.get_employees_with_birthdays_this_month()

        payments_summary_data = self.get_invoice_payment_summary(date_from=date_from, date_to=date_to)
        chart_loader_data['payments_summary'] = payments_summary_data

        return chart_loader_data
    