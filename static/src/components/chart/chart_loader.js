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

    renderChart() {
        if (this.Chart) {
            this.chartInstance.destroy()
        }
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
                            hoverOffset: 4
                        }
                    ]
                },
                options: {
                    indexAxis: this.props.axis,
                    responsive: true,
                    radius: '100%',
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
                    }
                },
            }
        );
    }
}

ChartLoader.template = "odoo_dashboard.ChartLoader"