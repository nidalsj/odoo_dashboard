/** @odoo-module **/
import { Component } from "@odoo/owl";

export class KpiCard extends Component {
    static template = "odoo_dashboard.KpiCard";
    static props = ["name", "icon", "value", "color"];
}