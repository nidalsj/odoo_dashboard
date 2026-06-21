/** @odoo-module */
import { registry } from '@web/core/registry';
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";
import { KpiCard } from '../kpi_card/kpi_card';
import { loadJS } from "@web/core/assets"
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { ChartLoader } from '../chart/chart_loader';


const { Component, useState, onWillStart, onMounted, useRef } = owl;

export class OdooDashboard extends Component {

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.task_model = "dashboard.tasks"
        this.searchInput = useRef("search-input")
        this.state = useState({
            period: 0,
            date: {date_from: "", date_to: ""},
            total_sales: {value:0, bg_color: "", text_color: ""},
            total_purchases: {value:0, bg_color: "", text_color: ""},
            total_customers: {value:0, bg_color: "", text_color: ""},
            sale_orders_today: {value:0, bg_color: "", text_color: ""},
            deliveryTodayChart: {labels: [], values: []},
            saleMonthlyChart: {labels: [], values: []},
            topProductsChart: {labels: [], values: []},
            topCustomersChart: {labels: [], values: []},
            chartColors: {
                delivery_chart: "",
                order_chart: "",
                customer_chart: "",
            },
            employeeBirthdays: [],
            paymentsSummary: [],
            stockReport: [],
            task:{name:"", completed:false},
            taskList:[],
            isEdit: false,
            activeId: false,
        })

        onWillStart(async ()=>{
            await loadJS("https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.29.4/moment.min.js")
            await this.getDateFilters()
            await this.getActiveSessionInfo()
            await this.getAllTasks()
            await this.loadCustomColors()
        })

        onMounted(() => {
            this.getKpiCardData()
            this.getChartLoaderData()
            this.getTableData()
        })
    }

    // *********************************
    // FETCHING DASHBOARD CONFIGURATIONS
    // *********************************

    async getActiveSessionInfo(){
        const sessionInfo = await this.orm.call("dashboard.handler", "get_active_session_info", [{}]);
        this.state.user = sessionInfo['user']
    }

    async loadCustomColors() {
        const keys = [
            "total_sales_card_color", "total_sales_text_color",
            "total_purchases_card_color", "total_purchases_text_color",
            "total_customers_card_color", "total_customers_text_color",
            "sales_today_card_color", "sales_today_text_color",
            "delivery_chart_color", "sale_orders_chart_color", "top_customers_chart_color"
        ]
    
        const prefixedKeys = keys.map(k => `dashboard_settings.${k}`);
        const params = await this.orm.call("ir.config_parameter", "search_read", [[["key", "in", prefixedKeys]], ["key", "value"]])
    
        const get = (key, fallback) => {
            const entry = params.find(p => p.key === `dashboard_settings.${key}`);
            return entry?.value || fallback;
        }
    
        this.state.total_sales = {
            ...this.state.total_sales,
            bg_color: get("total_sales_card_color", "#dc3545"),
            text_color: get("total_sales_text_color", "#ffffff")
        }
    
        this.state.total_purchases = {
            ...this.state.total_purchases,
            bg_color: get("total_purchases_card_color", "#17a2b8"),
            text_color: get("total_purchases_text_color", "#ffffff")
        }
    
        this.state.total_customers = {
            ...this.state.total_customers,
            bg_color: get("total_customers_card_color", "#6f42c1"),
            text_color: get("total_customers_text_color", "#ffffff")
        }
    
        this.state.sale_orders_today = {
            ...this.state.sale_orders_today,
            bg_color: get("sales_today_card_color", "#28a745"),
            text_color: get("sales_today_text_color", "#ffffff")
        }
    
        this.state.chartColors = {
            delivery: get("delivery_chart_color", "#42c5f5"),
            order: get("sale_orders_chart_color", "#f75b3b"),
            plan_choice: get("top_customers_chart_color", "#ffce56")
        }
    }

    // ********************
    // APPLYING DATE FILTER
    // ********************

    async getDateFilters() {
        const filters = await this.orm.searchRead("dashboard.date.filter", [], ["filter_name", "filter_days"]);
        this.state.dateFilters = filters;
    }

    onSelectFilter(filter) {
        this.state.selectedFilterName = filter.filter_name
        this.state.period = filter.filter_days
        this.onChangePeriod()
    }

    async onChangePeriod(){
        this.getDates()
        await this.getKpiCardData()
        // await this.getChartRenderData()
        // await this.getTableData()
    }

    getDates(){
        this.state.date = {
            date_from: moment().subtract(this.state.period, 'days').format('YYYY-MM-DD'),
            date_to: moment().format('YYYY-MM-DD'),
        }
    }

    // ************************************************
    // FETCHING VALUES FOR KPI CARDS, CHARTS AND TABLES
    // ************************************************

    async getKpiCardData(){
        const params = {
            'date_from': this.state.date.date_from,
            'date_to': this.state.date.date_to
        }
        const kpiCardData = await this.orm.call("dashboard.handler", "get_dashboard_kpi_card_data", [], params);
        this.state.total_sales.value = kpiCardData['total_sales']
        this.state.total_purchases.value = kpiCardData['total_purchases']
        this.state.total_customers.value = kpiCardData['total_customers']
        this.state.sale_orders_today.value = kpiCardData['sales_orders_today']

        this.state.salesDomain = kpiCardData['sales_domain']
        this.state.purchaseDomain = kpiCardData['purchase_domain']
        this.state.totalCustomersDomain = kpiCardData['customers_domain']
        this.state.salesTodayDomain = kpiCardData['sales_today_domain']
    }

    async getChartLoaderData(){
        const chartLoaderData = await this.orm.call("dashboard.handler", "get_dashboard_chart_loader_data", [{}]);
        this.state.deliveryTodayChart.labels = chartLoaderData.delivery_labels
        this.state.deliveryTodayChart.values = chartLoaderData.delivery_values

        this.state.saleMonthlyChart.labels = chartLoaderData.order_labels
        this.state.saleMonthlyChart.values = chartLoaderData.order_values

        this.state.topProductsChart.labels = chartLoaderData.products_labels
        this.state.topProductsChart.values = chartLoaderData.products_values

        this.state.topCustomersChart.labels = chartLoaderData.customers_labels
        this.state.topCustomersChart.values = chartLoaderData.customers_values
    }

    async getTableData(){
        const tableData = await this.orm.call("dashboard.handler", "get_dashboard_chart_loader_data", [{}]);
        this.state.employeeBirthdays = tableData.employee_birthdays
        this.state.paymentsSummary = tableData.payments_summary
    }

    // ************************
    // TASK MANAGEMENT SECTION
    // ************************

    async getAllTasks(){
        this.state.taskList = await this.orm.searchRead(this.task_model, [], ["name", "completed"])
    }

    addTask(){
        this.resetForm()
        this.state.activeId = false
        this.state.isEdit = false
    }

    editTask(task){
        this.state.activeId = task.id
        this.state.isEdit = true
        this.state.task = {...task}
    }

    async saveTask(){
        if (!this.state.isEdit){
            await this.orm.create(this.task_model, [this.state.task])
            this.resetForm()
        } else {
            await this.orm.write(this.task_model, [this.state.activeId], this.state.task)
            this.resetForm()
        }
        await this.getAllTasks()
    }

    resetForm(){
        this.state.task = {name:"", completed:false}
        this.state.activeId = false
        this.state.isEdit = false
    }

    async deleteTask(task){
        await this.orm.unlink(this.task_model, [task.id])
        await this.getAllTasks()
    }

    async searchTasks(){
        const text = this.searchInput.el.value
        this.state.taskList = await this.orm.searchRead(this.task_model, [['name','ilike',text]], ["name", "completed"])
    }

    async toggleTask(e, task){
        await this.orm.write(this.task_model, [task.id], {completed: e.target.checked})
        await this.getAllTasks()
    }

    // ***********************************************
    // HANDLING KPI CARD CLICKS TO OPEN RELEVANT VIEWS
    // ***********************************************

    async viewTotalSales() {
        return this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Sales Orders',
            res_model: 'sale.order',
            view_mode: 'list,form',
            views: [[false, 'list'], [false, 'form']],
            domain: this.state.salesDomain
        });
    }

    async viewTotalPurchases() {
        return this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Purchases Orders',
            res_model: 'purchase.order',
            view_mode: 'list,form',
            views: [[false, 'list'], [false, 'form']],
            domain: this.state.purchaseDomain
        });
    }

    async viewCustomers() {
        return this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Customers',
            res_model: 'res.partner',
            view_mode: 'list,form',
            views: [[false, 'list'], [false, 'form']],
            domain: this.state.totalCustomersDomain
        });
    }

    async viewSalesToday() {
        return this.action.doAction({
            type: 'ir.actions.act_window',
            name: 'Sales Orders Today',
            res_model: 'sale.order',
            view_mode: 'list,form',
            views: [[false, 'list'], [false, 'form']],
            domain: this.state.salesTodayDomain
        });
    }

}

OdooDashboard.template = "odoo_dashboard.OdooDashboard"
OdooDashboard.components = { KpiCard, Dropdown, DropdownItem, ChartLoader }
registry.category("actions").add("odoo_dashboard", OdooDashboard)
