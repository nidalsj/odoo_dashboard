/** @odoo-module */
import { Component, onWillStart, useRef, useEffect } from "@odoo/owl";
import { loadBundle } from "@web/core/assets";
import { useService } from "@web/core/utils/hooks";

const DOUGHNUT_COLORS = [
    "#3b82f6", "#f97316", "#10b981", "#ef4444", "#8b5cf6",
    "#eab308", "#06b6d4", "#ec4899", "#84cc16", "#64748b",
];

export class ChartLoader extends Component {
    static template = "odoo_dashboard.ChartLoader";
    static props = ["type", "title", "labels", "data", "domains", "model", "datasetLabel", "axis?", "color?"];

    setup() {
        this.action = useService("action");
        this.chartRef = useRef("chart");

        onWillStart(() => loadBundle("web.chartjs_lib"));

        // DRAW THE CHART WHEN COMPONENT IS MOUNTED AND DRAW IT AGAIN WHEN DATA CHANGES
        useEffect(
            () => {
                this.renderChart();
                return () => this.chart.destroy();
            },
            () => [this.props.labels, this.props.data]
        );
    }

    renderChart() {
        this.chart = new Chart(this.chartRef.el, {
            type: this.props.type,
            data: {
                labels: [...this.props.labels],
                datasets: [{
                    label: this.props.datasetLabel,
                    data: [...this.props.data],
                    backgroundColor: this.props.color || DOUGHNUT_COLORS,
                    hoverOffset: 4,
                }],
            },
            options: {
                indexAxis: this.props.axis,
                responsive: true,
                onHover: (event, elements) => {
                    event.native.target.style.cursor = elements.length ? "pointer" : "default";
                },
                onClick: (event, elements) => {
                    if (elements.length) {
                        this.viewRecords(elements[0].index);
                    }
                },
                plugins: {
                    legend: {
                        position: "bottom",
                        display: this.props.type === "doughnut",
                    },
                },
            },
        });
    }

    viewRecords(index) {
        this.action.doAction({
            type: "ir.actions.act_window",
            name: this.props.title,
            res_model: this.props.model,
            domain: this.props.domains[index],
            views: [[false, "list"], [false, "form"]],
        });
    }
}
