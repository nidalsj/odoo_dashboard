# Odoo 18 Business Dashboard

A modern and interactive business intelligence dashboard built for **Odoo 18** to provide real-time insights into sales, purchases, customers, inventory, and business operations.

Built using **OWL, Python, PostgreSQL, and Chart.js**, this dashboard provides dynamic analytics, customizable UI components, date-based filtering, and interactive drill-down capabilities.

Users can customize dashboard views, apply date filters, and open related Odoo records directly from KPI cards and charts.

---

# Features

# 👉 KPI Cards

Quick business overview with real-time calculations and clickable drill-down actions.

### Total Sales
Displays confirmed sales amount based on the selected date period.

### Total Purchases
Shows confirmed purchase amount during the selected date range.

### Customers
Displays customers who placed orders within the selected period.

### Sales Today
Shows today's confirmed sales orders with direct access to today's sales records.

---

# 👉 Interactive Charts

## Delivery Status Analysis

Displays today's delivery operations grouped by delivery status.

Includes:

- Ready
- Waiting
- Done
- Cancelled

Clicking a status opens the related delivery records.

---

## Monthly Sales Order Report

Year-based sales performance tracking.

Features:

- Starts from January of the current year
- Updates automatically until the current month
- Monthly order comparison
- Clickable months for detailed sales records

---

## Top Products

Displays products with the highest sales performance.

Features:

- Filters data based on selected period
- Shows product performance comparison
- Clicking a product opens related sales orders containing that product

---

## Top Customers

Shows customers with the highest purchase value during the selected period.

Useful for:

- Identifying valuable customers
- Customer analysis
- Creating customer-specific offers and discounts

---

# 👉 Reports & Productivity Widgets

## Employee Birthday Widget

A small productivity widget showing upcoming employee birthdays.

Helps teams:

- Remember employee birthdays
- Improve workplace engagement

---

## Task Manager

A lightweight productivity tool inside the dashboard.

Features:

- Create tasks
- Update tasks
- Mark tasks as completed
- Track daily activities

---

## Invoice Payment Summary

Company-wide invoice analysis.

Displays:

- Total invoiced amount
- Paid amount
- Pending amount

---

# 👉 Technical Stack

<p>
<img src="https://img.shields.io/badge/Odoo-18-purple"/>
<img src="https://img.shields.io/badge/Python-blue"/>
<img src="https://img.shields.io/badge/PostgreSQL-336791"/>
<img src="https://img.shields.io/badge/JavaScript-yellow"/>
<img src="https://img.shields.io/badge/OWL-red"/>
<img src="https://img.shields.io/badge/Chart.js-orange"/>
</p>

---

# 👉 Architecture

```text
dashboard_module/
├── models/
├── views/
├── static/
│   ├── src/js/
│   ├── src/xml/
│   └── src/css/
├── security/
└── __manifest__.py
```


---

# 👉 Key Highlights

- Dynamic date range filtering
- Customizable dashboard colors
- OWL-based interactive UI
- Chart.js visual analytics
- Clickable drill-down reports
- ORM and SQL reporting
- Sales analytics
- Customer analytics
- Inventory insights
- Multi-company invoice summary
- Productivity widgets

---

# 👉 Installation

Clone this repository into your Odoo custom addons directory:

```bash
git clone https://github.com/nidalsj/odoo_dashboard.git
```

Move into your Odoo project directory:

```bash
cd odoo
```

Restart Odoo server and update the module:

```bash
./odoo-bin -c odoo.conf -u odoo_dashboard
```

or from Odoo UI:

```
Apps → Update Apps List → Install Odoo 18 Business Dashboard
```

---

# 👉 Customization

This dashboard is designed to be extended and customized according to business requirements.

You can customize:

- KPI cards
- Dashboard colors
- Date filter options
- Charts and analytics
- Business reports
- Drill-down actions
- Additional widgets

The module structure allows developers to easily add new models, OWL components, reports, and dashboard features.

Feel free to fork this project and adapt it for your own Odoo implementations.

---

# 👉 Screenshots

<img width="1769" height="889" alt="Image" src="https://github.com/user-attachments/assets/2a2e0cb3-c9d7-4890-9ed4-416c1c7ab426" />
<img width="1920" height="964" alt="Image" src="https://github.com/user-attachments/assets/5506c2ec-d969-483d-81af-66995f1c41f7" />
<img width="1920" height="964" alt="Image" src="https://github.com/user-attachments/assets/4393b898-99bc-4b27-9088-930647148bed" />

---

# 👨‍💻 Developer

**Nidal SJ**

Odoo Developer | Python Developer | ERP Solutions
