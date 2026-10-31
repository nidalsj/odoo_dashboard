/** @odoo-module */
import { Component, useState, onWillStart, useRef } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { user } from "@web/core/user";
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";
import { KpiCard } from "../kpi_card/kpi_card";
import { ChartLoader } from "../chart/chart_loader";

const emptyKpi = () => ({ value: 0, domain: [] });
const emptyChart = () => ({ labels: [], values: [], domains: [] });

export class OdooDashboard extends Component {

    setup() {
        this.orm = useService("orm");
        this.action = useService("action");
        this.task_model = "dashboard.tasks"
        this.searchInput = useRef("search-input")
        this.userName = user.name
        this.state = useState({
            period: null,
            kpis: {
                total_sales: emptyKpi(),
                total_purchases: emptyKpi(),
                total_customers: emptyKpi(),
                sales_today: emptyKpi(),
            },
            charts: {
                delivery: emptyChart(),
                monthly_sales: emptyChart(),
                top_products: emptyChart(),
                top_customers: emptyChart(),
            },
            dateFilters: [],
            employeeBirthdays: [],
            paymentsSummary: [],
            task:{name:"", completed:false},
            taskList:[],
            isEdit: false,
            activeId: false,
        })

        onWillStart(async () => {
            await Promise.all([
                this.getDateFilters(),
                this.getAllTasks(),
                this.loadDashboardData(),
            ])
        })
    }

    // ********************
    // APPLYING DATE FILTER
    // ********************

    async getDateFilters() {
        this.state.dateFilters = await this.orm.searchRead("dashboard.date.filter", [], ["filter_name", "filter_days"]);
    }

    async onSelectFilter(filter) {
        this.state.selectedFilterName = filter.filter_name
        this.state.period = filter.filter_days
        await this.loadDashboardData()
    }

    // ************************************************
    // FETCHING DATA FOR KPI CARDS, CHARTS AND TABLES
    // ************************************************

    async loadDashboardData() {
        const params = { period: this.state.period }
        const [kpis, charts, tables] = await Promise.all([
            this.orm.call("dashboard.handler", "get_dashboard_kpi_card_data", [], params),
            this.orm.call("dashboard.handler", "get_dashboard_chart_loader_data", [], params),
            this.orm.call("dashboard.handler", "get_dashboard_table_data", [], params),
        ])
        this.state.kpis = kpis
        this.state.charts = charts
        this.state.employeeBirthdays = tables.employee_birthdays
        this.state.paymentsSummary = tables.payments_summary
    }

    // ********************************
    // HANDLING KPI CARD ONCLICK EVENTS
    // ********************************

    viewRecords(name, model, domain) {
        return this.action.doAction({
            type: 'ir.actions.act_window',
            name: name,
            res_model: model,
            views: [[false, 'list'], [false, 'form']],
            domain: domain,
        });
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

    // ******************************
    // HANDLING TABLE ON CLICK EVENTS 
    // ******************************

    editEmployee(employeeId) {
        this.env.services.action.doAction({
            type: "ir.actions.act_window",
            name: "Employee",
            res_model: "hr.employee",
            res_id: employeeId,
            views: [[false, "form"]],
            target: "current",
        });
    }

}

OdooDashboard.template = "odoo_dashboard.OdooDashboard"
OdooDashboard.components = { KpiCard, Dropdown, DropdownItem, ChartLoader }
registry.category("actions").add("odoo_dashboard", OdooDashboard)
