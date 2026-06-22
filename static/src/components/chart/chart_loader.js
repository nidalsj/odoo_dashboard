/** @odoo-module */

import { registry } from "@web/core/registry"
import { loadJS } from "@web/core/assets"
const { Component, onWillStart, useRef, onMounted, useEffect } = owl

export class ChartLoader extends Component {
    setup() {
        this.chartRef = useRef("chart")
        onWillStart(async () => {
            await loadJS("https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js")
        })

        onMounted(() => this.renderChart())

        // Rerender chart when props change
        useEffect(() => {
            if (this.chartInstance) {
                this.chartInstance.destroy()
            }
            this.renderChart(); // Re-render chart with new data
        }, () => [this.props.labels, this.props.data, this.props.datasetLabel])
    }

    getDynamicColors(count) {
        if (this.props.color?.length) return this.props.color;
        return Array.from({ length: count }, (_, i) =>
            `hsl(${Math.round((360 / count) * i)}, 70%, 60%)`
        );
    }

    renderChart() {
        if (this.Chart) {
            this.chartInstance.destroy()
        }
        let backgroundColors = this.getDynamicColors(this.props.labels.length);
        let showLegend = this.props.type === "doughnut";
        this.chartInstance = new Chart(this.chartRef.el,
            {
                type: this.props.type,
                data: {
                    labels: this.props.labels,
                    datasets: [
                        {
                            label: this.props.datasetLabel || "Label Unavailable",
                            data: this.props.data || [],
                            backgroundColor: backgroundColors,
                            hoverOffset: 4
                        }
                    ]
                },
                options: {
                    indexAxis: this.props.axis,
                    responsive: true,
                    radius: '100%',
                    onHover: (event, elements) => {
                        event.native.target.style.cursor = elements.length > 0 ? 'pointer' : 'default';
                    },
                    plugins: {
                        legend: {
                            position: 'bottom',
                            display: showLegend,
                        },
                        title: {
                            display: false,
                            text: this.props.title,
                            position: 'bottom',
                        }
                    },
                    onClick: (event, elements) => {
                        if (elements.length > 0) {
                            const index = elements[0].index;
                            const label = this.props.labels[index];
                            this.onChartClick(label);
                        }
                    },
                },
            }
        );
    }

    onChartClick(label) {

        if (!this.props.model) return;
        let domain = [...(this.props.domain || [])];

        // Delivery status filter
        if (this.props.title === "Deliveries") {
            const statusMap = {
                "Draft": "draft",
                "Waiting": "waiting",
                "Ready": "assigned",
                "Done": "done",
                "Cancelled": "cancel"
            }

            if (statusMap[label]) {
                domain.push(["state","=",statusMap[label]]);
            }
        }

        // Sales by month filter
        if (this.props.title === "Monthly Sales") {
            let recordIds = this.props.recordIds[label] || [];
            if (recordIds.length) {
                domain.push(["id","in",recordIds]);
            }
        }

        this.env.services.action.doAction({
            type: "ir.actions.act_window",
            name: this.props.title,
            res_model: this.props.model,
            domain: domain,
            context: {group_by: this.props.groupBy? [this.props.groupBy]: []},
            views: [[false, "list"],[false, "form"]]
        });
    }
}

ChartLoader.template = "odoo_dashboard.ChartLoader"