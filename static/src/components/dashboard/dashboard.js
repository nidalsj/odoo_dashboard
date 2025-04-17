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
        this.task_model = "dashboard.tasks"
        this.searchInput = useRef("search-input")
        this.state = useState({
            period: 0,
            total_customers: {value:0},
            total_sales: {value:0},
            total_purchases: {value:0},
            sale_orders_today: {value:0},
            deliveryTodayChart: {labels: [], values: []},
            saleMonthlyChart: {labels: [], values: []},
            topProductsChart: {labels: [], values: []},
            topCustomersChart: {labels: [], values: []},
            employeeBirthdays: [],
            paymentsSummary: [],
            stockReport: [],
            task:{name:"", completed:false},
            taskList:[],
            isEdit: false,
            activeId: false,
        })

        onWillStart(async ()=>{
            await loadJS("https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.29.4/moment.min.js");
            await this.getDateFilters()
            await this.getActiveSessionInfo()
            await this.getAllTasks()
        })

        onMounted(() => {
            this.getKpiCardData()
            this.getChartLoaderData()
            this.getTableData()
        })
    }

    async getActiveSessionInfo(){
        const sessionInfo = await this.orm.call("dashboard.handler", "get_active_session_info", [{}]);
        this.state.user = sessionInfo['user']
    }

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
        console.log(this.state.date)
        // await this.getTileData()
        // await this.getChartRenderData()
        // await this.getTableData()
    }

    getDates(){
        this.state.date = moment().subtract(this.state.period, 'days').format('YYYY-MM-DD')
    }

    // ************************************************
    // FETCHING VALUES FOR KPI CARDS, CHARTS AND TABLES
    // ************************************************

    async getKpiCardData(){
        const kpiCardData = await this.orm.call("dashboard.handler", "get_dashboard_kpi_card_data", [{}]);
        this.state.total_sales.value = kpiCardData['total_sales']
        this.state.total_purchases.value = kpiCardData['total_purchases']
        this.state.total_customers.value = kpiCardData['total_customers']
        this.state.sale_orders_today.value = kpiCardData['sales_orders_today']
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
    // TASKS MANAGEMENT SECTION
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

}

OdooDashboard.template = "odoo_dashboard.OdooDashboard"
OdooDashboard.components = { KpiCard, Dropdown, DropdownItem, ChartLoader }
registry.category("actions").add("odoo_dashboard", OdooDashboard)
