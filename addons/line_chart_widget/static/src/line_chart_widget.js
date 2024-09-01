/** @odoo-module **/

import { _lt } from "@web/core/l10n/translation";
import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
import { loadJS } from "@web/core/assets";
import { format } from "web.field_utils";
import {
    Component,
    onWillStart,
    onWillRender,
    onMounted,
    onWillUnmount,
    useRef,
    useState,
    onWillPatch,
    onWillUpdateProps,
    onPatched,
} from "@odoo/owl";

export class LineChartField extends Component {
    setup() {
        super.setup();
        this.canvasRef = useRef("canvas");
        this.containerRef = useRef("container");
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
        const formatter = format[formatterType];
        if (formatterType === "date" || formatterType === "datetime") {
            v = moment(v);
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
        this.chart = new Chart(this.canvasRef.el, {
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
        const relationField = this.props.field.relation_field;
        const modelName = this.props.field.relation;
        // <expression for form views> || <expression for kanban views>
        const parent_id = this.props.value.model.root.resId || this.props.value.parentRecord.resId;
        const data = await this.orm.searchRead(
            modelName,
            [[relationField, "=", parent_id]],
            this.props.dataFields
        );
        this.data = data;
    }
}

LineChartField.template = "line_chart_widget.LineChartWidget";
LineChartField.displayName = _lt("Line Chart Field");
LineChartField.supportedTypes = ["one2many"];
LineChartField.extractProps = ({ attrs, field }) => {
    const defaultChartOptions = {
        responsieve: true,
        maintainAspectRatio: false,
        legend: {
            display: true,
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
        dataFields: attrs.options.dataFields || [],
        chartOptions: { ...defaultChartOptions, ...attrs.options.chartOptions },
        datasetOptions: { ...defaultDatasetOptions, ...attrs.options.datasetOptions },
    };
};

registry.category("fields").add("line_chart", LineChartField);
