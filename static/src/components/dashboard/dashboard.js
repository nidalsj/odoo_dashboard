/** @odoo-module */
import { registry } from '@web/core/registry';
import { useService } from "@web/core/utils/hooks";

const { Component, useState, onWillStart, onMounted } = owl;

export class OdooDashboard extends Component {

    

}

OdooDashboard.template = "odoo_dashboard.OdooDashboard"
OdooDashboard.components = {}
registry.category("actions").add("odoo_dashboard", OdooDashboard)
