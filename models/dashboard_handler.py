from datetime import date, datetime, time, timedelta
import pytz
from dateutil.relativedelta import relativedelta
from odoo import api, fields, models
from odoo.tools import format_amount


class DashboardHandler(models.Model):
    _name = "dashboard.handler"
    _description = "Prepare Data for Dashboard"

    def _get_dates(self, period=None):
        if period is None:
            return None, None
        today = fields.Date.context_today(self)
        return today - timedelta(days=period), today

    def _date_domain(self, field_name, date_from=None, date_to=None):
        tz = pytz.timezone(self.env.context.get('tz') or self.env.user.tz or 'UTC')
        domain = []
        if date_from:
            start = tz.localize(datetime.combine(date_from, time.min)).astimezone(pytz.utc)
            domain.append((field_name, '>=', fields.Datetime.to_string(start)))
        if date_to:
            end = tz.localize(datetime.combine(date_to, time.max)).astimezone(pytz.utc)
            domain.append((field_name, '<=', fields.Datetime.to_string(end)))
        return domain

    # CARDS DATA

    @api.model
    def get_dashboard_kpi_card_data(self, period=None):
        currency = self.env.company.currency_id
        date_from, date_to = self._get_dates(period)
        today = fields.Date.context_today(self)

        sales_domain = [('state', '=', 'sale')] + self._date_domain('date_order', date_from, date_to)
        sales_orders = self.env['sale.order'].search(sales_domain)

        purchase_domain = [('state', '=', 'purchase')] + self._date_domain('date_order', date_from, date_to)
        purchase_orders = self.env['purchase.order'].search(purchase_domain)

        customers = sales_orders.partner_id

        sales_today_domain = [('state', '=', 'sale')] + self._date_domain('date_order', today, today)

        return {
            'total_sales': {
                'value': format_amount(self.env, sum(sales_orders.mapped('amount_total')), currency),
                'domain': sales_domain,
            },
            'total_purchases': {
                'value': format_amount(self.env, sum(purchase_orders.mapped('amount_total')), currency),
                'domain': purchase_domain,
            },
            'total_customers': {
                'value': len(customers),
                'domain': [('id', 'in', customers.ids)],
            },
            'sales_today': {
                'value': self.env['sale.order'].search_count(sales_today_domain),
                'domain': sales_today_domain,
            },
        }

    # CHARTS DATA

    def _get_deliveries_today_chart_data(self):
        Picking = self.env['stock.picking']
        today = fields.Date.context_today(self)
        domain = self._date_domain('scheduled_date', today, today)

        counts = dict(Picking._read_group(domain, ['state'], ['__count']))
        statuses = [
            (state, label) for state, label in Picking._fields['state']._description_selection(self.env)
            if counts.get(state)
        ]
        return {
            'labels': [label for state, label in statuses],
            'values': [counts[state] for state, label in statuses],
            'domains': [domain + [('state', '=', state)] for state, label in statuses],
        }

    def _get_monthly_sales_chart_data(self, period=None):
        today = fields.Date.context_today(self)
        date_from, date_to = self._get_dates(period)
        date_from = date_from or today.replace(month=1, day=1)
        date_to = date_to or today
        label_format = '%b' if date_from.year == date_to.year else '%b %Y'

        labels, values, domains = [], [], []
        month_start = date_from.replace(day=1)
        while month_start <= date_to:
            month_end = month_start + relativedelta(months=1, days=-1)
            domain = [('state', '=', 'sale')] + self._date_domain(
                'date_order', max(month_start, date_from), min(month_end, date_to))
            labels.append(month_start.strftime(label_format))
            values.append(self.env['sale.order'].search_count(domain))
            domains.append(domain)
            month_start += relativedelta(months=1)

        return {'labels': labels, 'values': values, 'domains': domains}

    def _get_top_products_chart_data(self, date_from=None, date_to=None):
        order_domain = [('state', '=', 'sale')] + self._date_domain('date_order', date_from, date_to)
        line_domain = [('product_id', '!=', False)] + [
            ('order_id.' + leaf[0], leaf[1], leaf[2]) for leaf in order_domain
        ]
        groups = self.env['sale.order.line']._read_group(
            line_domain, ['product_id'], ['price_subtotal:sum'], order='price_subtotal:sum desc', limit=10)
        return {
            'labels': [product.display_name for product, amount in groups],
            'values': [amount for product, amount in groups],
            'domains': [order_domain + [('order_line.product_id', '=', product.id)] for product, amount in groups],
        }

    def _get_top_customers_chart_data(self, date_from=None, date_to=None):
        order_domain = [('state', '=', 'sale')] + self._date_domain('date_order', date_from, date_to)
        groups = self.env['sale.order']._read_group(
            order_domain, ['partner_id'], ['amount_total:sum'], order='amount_total:sum desc', limit=5)
        return {
            'labels': [partner.display_name for partner, amount in groups],
            'values': [amount for partner, amount in groups],
            'domains': [order_domain + [('partner_id', '=', partner.id)] for partner, amount in groups],
        }

    @api.model
    def get_dashboard_chart_loader_data(self, period=None):
        date_from, date_to = self._get_dates(period)
        return {
            'delivery': self._get_deliveries_today_chart_data(),
            'monthly_sales': self._get_monthly_sales_chart_data(period),
            'top_products': self._get_top_products_chart_data(date_from, date_to),
            'top_customers': self._get_top_customers_chart_data(date_from, date_to),
        }

    # TABLES DATA

    def get_employees_with_birthdays_this_month(self):
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
    def get_dashboard_table_data(self, period=None):
        date_from, date_to = self._get_dates(period)
        return {
            'employee_birthdays': self.get_employees_with_birthdays_this_month(),
            'payments_summary': self.get_invoice_payment_summary(date_from=date_from, date_to=date_to),
        }