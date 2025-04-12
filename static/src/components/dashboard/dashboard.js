/** @odoo-module */
import { registry } from '@web/core/registry';
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";
import { session } from "@web/session";
import { KpiCard } from '../kpi_card/kpi_card';
import { loadJS } from "@web/core/assets"
import { Dropdown } from "@web/core/dropdown/dropdown";
import { DropdownItem } from "@web/core/dropdown/dropdown_item";


const { Component, useState, onWillStart, onMounted } = owl;

export class OdooDashboard extends Component {

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            period: 0,
            total_customers: {value:0},
            total_sales: {value:0},
            total_purchases: {value:0},
            sale_orders_today: {value:0},
            driverOrderCounts: {labels: [], values: []},
            orderReportCounts: {labels: [], values: []},
            packageReportCounts: {labels: [], values: []},
            choiceReportCounts: {labels: [], values: []},
            customerBirthdays: [],
            paymentReport: [],
            user: session.partner_display_name,

        });

        onWillStart(async ()=>{
            await loadJS("https://cdnjs.cloudflare.com/ajax/libs/moment.js/2.29.4/moment.min.js");
            await this.fetchDateFilters()
        })

        onMounted(() => {
            this.getKpiCardData()
        })
    }

    async fetchDateFilters() {
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

    async getKpiCardData(){
        const kpiCardData = await this.orm.call("dashboard.handler", "get_kpi_card_data", [{}]);
        this.state.total_sales.value = kpiCardData['total_sales']
        this.state.total_purchases.value = kpiCardData['total_purchases']
        this.state.total_customers.value = kpiCardData['total_customers']
        this.state.sale_orders_today.value = kpiCardData['sales_orders_today']


    }

}

OdooDashboard.template = "odoo_dashboard.OdooDashboard"
OdooDashboard.components = { KpiCard, Dropdown, DropdownItem }
registry.category("actions").add("odoo_dashboard", OdooDashboard)
