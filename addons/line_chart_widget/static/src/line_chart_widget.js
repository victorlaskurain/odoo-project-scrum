/** @odoo-module **/

import { _t } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { loadJS } from "@web/core/assets";
import {
    Component,
    onWillStart,
    onWillRender,
    onMounted,
    onWillUnmount,
    signal,
    useState,
    onWillPatch,
    onWillUpdateProps,
    onPatched,
} from "@odoo/owl";
import { deserializeDate, deserializeDateTime } from "@web/core/l10n/dates";

const formatters = registry.category("formatters");

export class LineChartField extends Component {
    static template = "line_chart_widget.LineChartWidget";

    setup() {
        super.setup();
        this.canvas = signal.ref();
        this.data = [];
        this.chart = null;
        this.orm = useService("orm");
        onWillStart(() => {
            return loadJS(["/web/static/lib/Chart/Chart.js"]);
        });
        onWillStart(() => this.loadData());
        onMounted(() => this.renderChart());
        onWillUpdateProps(() => this.loadData());
        onPatched(() => this.renderChart());
        onWillUnmount(() => this.destroyChart());
    }

    formatXLabel(v) {
        const xLabelFieldName = this.props.dataFields[0];
        const xLabelFieldDef = this.props.datasetOptions[xLabelFieldName] || {};
        const formatterType = xLabelFieldDef["format"] || "char";
        let formatter = formatters.get(formatterType);
        if (formatterType === "date") {
            formatter = formatters.get("datetime");
            v = deserializeDate(v)
            return formatter(v, {numeric: true, showTime: false});
        }
        if (formatterType === "datetime") {
            v = deserializeDateTime(v, {numeric: true});
        }
        return formatter(v);
    }

    renderChart() {
        this.destroyChart();
        const labelsField = this.props.dataFields[0];
        const labels = this.data.map((item) => item[labelsField]).map(this.formatXLabel.bind(this));
        const datasets = this.props.dataFields.slice(1).map((fieldName) => {
            let dataset = this.props.datasetOptions[fieldName] || {};
            dataset.data = this.data.map((r) => r[fieldName]);
            return dataset;
        });
        this.chart = new Chart(this.canvas(), {
            type: "line",
            options: this.props.chartOptions,
            data: {
                labels: labels,
                datasets: datasets,
            },
        });
    }

    destroyChart() {
        if (this.chart) {
            this.chart.destroy();
        }
    }

    async loadData() {
        const field = this.props.record.fields[this.props.name];
        const relationField = field.relation_field;
        const modelName = field.relation;
        // <expression for form views> || <expression for kanban views>
        const parent_id = this.props.record.evalContext.id;
        const data = await this.orm.searchRead(
            modelName,
            [[relationField, "=", parent_id]],
            this.props.dataFields,
        );
        this.data = data;
    }
}

registry.category("fields").add("line_chart", {
    component: LineChartField,
    displayName: _t("Line Chart Field"),
    supportedTypes: ["one2many"],
    extractProps: ({ attrs, field, options }) => {
        const defaultChartOptions = {
            responsieve: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: true,
                },
            },
            animation: {},
            tooltips: {
                callbacks: {
                    label: function (tooltipItem, data) {
                        const dataset = data.datasets[tooltipItem.datasetIndex];
                        const formatterType = dataset.format || "float";
                        const formatter = format[formatterType];
                        var label = dataset.label || "";
                        if (label) {
                            label += ": ";
                        }
                        label += formatter(tooltipItem.yLabel);
                        return label;
                    },
                },
            },
        };
        const defaultDatasetOptions = {};
        return {
            field: field,
            dataFields: options.dataFields || [],
            chartOptions: { ...defaultChartOptions, ...options.chartOptions },
            datasetOptions: { ...defaultDatasetOptions, ...options.datasetOptions },
        };
    },
});
