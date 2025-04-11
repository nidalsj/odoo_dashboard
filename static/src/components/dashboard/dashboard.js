/** @odoo-module */
import { registry } from '@web/core/registry';
import { useService } from "@web/core/utils/hooks";
import { rpc } from "@web/core/network/rpc";
import { session } from "@web/session";
import { KpiCard } from '../kpi_card/kpi_card';


const { Component, useState, onWillStart, onMounted } = owl;

export class OdooDashboard extends Component {

    setup() {
        this.orm = useService("orm");
        this.state = useState({
            new_customers: {value:0},
            active_customers: {value:0},
            customers_today: {value:0},
            sales_today: {value:0},
            driverOrderCounts: {labels: [], values: []},
            orderReportCounts: {labels: [], values: []},
            packageReportCounts: {labels: [], values: []},
            choiceReportCounts: {labels: [], values: []},
            customerBirthdays: [],
            paymentReport: [],
            user: session.partner_display_name,

        });

        onMounted(() => {
            this.getKpiCardData()
        })
    }

    async getKpiCardData(){
        const total_customers = await this.orm.searchCount("res.partner",[])
        this.state.new_customers.value = total_customers

    }

}

OdooDashboard.template = "odoo_dashboard.OdooDashboard"
OdooDashboard.components = { KpiCard }
registry.category("actions").add("odoo_dashboard", OdooDashboard)
