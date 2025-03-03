/** @odoo-module **/
import { registry } from "@web/core/registry";
import { Component } from "@odoo/owl";
import { onMounted, useState } from "@odoo/owl";
import { useService } from "@web/core/utils/hooks";
import { loadJS } from "@web/core/assets";

// Define nextTick if not provided by OWL
const nextTick = () => new Promise((resolve) => setTimeout(resolve, 0));

class ShopifyClientAction extends Component {
    static template = "shopify_conector.dashboard";

    setup() {
        this.instances = useState([]);
        this.orm = useService("orm");
        this.action = useService("action");
        this.currentCharts = {};

        onMounted(async () => {
            await this.fetchInstances();
        });
    }

    async fetchInstances(instancesData = []) {
        const instances = await this.orm.call(
            "shopify.instance.ept",
            "get_active_instances",
            [[]],
            { instancesData }
        );
    
        this.instances.splice(0, this.instances.length, ...instances);
    
        await nextTick();
    
        for (let instance of instances) {
            if (this.currentCharts[instance.id]) {
                this.currentCharts[instance.id].destroy(); // Clear existing chart
            }
            this.currentCharts[instance.id] = await this.loadChart(instance.id, instance.sales_data);
        }
    }
    

    onFilterChange(event, instance) {
        const instanceContainers = document.querySelectorAll('.card_d1'); 
        let instancesData = [];
        instanceContainers.forEach(container => {
            const select = container.querySelector('.form-control');
            if (select) {
                const instanceId = parseInt(select.getAttribute("data-instance-id"));
                const period = select.value;
                if (!isNaN(instanceId)) {
                    instancesData.push({ id: instanceId, period: period });
                }
            }
        });
        this.fetchInstances(instancesData); 
    }
    
    

    async loadChart(instanceId, salesData) {
        await loadJS("https://cdn.jsdelivr.net/npm/chart.js");
        
        const ctx = await getCanvasElement(instanceId);
        if (!ctx) {
            console.error(`Canvas for instanceId ${instanceId} not found.`);
            return;
        }
    
        const chartConfig = {
            type: "line",
            data: {
                labels: salesData.dates,
                datasets: [{
                    label: "Sales Trend",
                    data: salesData.values,
                    borderColor: "#800000",
                    borderWidth: 1.5,
                    backgroundColor: "rgba(139,0,0,0.2)",
                    fill: "start",
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                scales: {
                    y: {
                        min: Math.min(...salesData.values) - 10,
                        max: Math.max(...salesData.values) + 10,
                        grid: { color: "rgba(0, 0, 0, 0.1)" },
                    },
                    x: {
                        ticks: { maxRotation: 45, minRotation: 45 },
                    },
                },
            }
        };
    
        return new Chart(ctx, chartConfig);
    }
    
    

    openOperationAction() {
        this.action.doAction("shopify_connector_inwi.operation_action");
    }
    openReportSection() {
        this.action.doAction("shopify_connector_inwi.common_log_lines_ept_data_action");
    }

    openproductSection(event) {
        const instanceId = event.currentTarget.dataset.instanceId;
        
        // this.action.doAction("shopify_connector.shopify_product_product_ept_action");
        this.action.doAction("shopify_connector_inwi.shopify_product_product_ept_action", {
            additionalContext: {
                default_instance_id: parseInt(instanceId), // Pass the instance ID to the context
            },
        });

    }

    opencustomerSection(event) {
        // this.action.doAction("shopify_connector.shopify_customer_action");

        const instanceId = event.currentTarget.dataset.instanceId;
        
        // this.action.doAction("shopify_connector.shopify_product_product_ept_action");
        this.action.doAction("shopify_connector_inwi.shopify_customer_action", {
            additionalContext: {
                default_instance_id: parseInt(instanceId), // Pass the instance ID to the context
            },
        });

    }
    opensalesSection() {
        this.action.doAction("shopify_connector_inwi.shopify_orders_action");
    }

    openrefundSection() {
        this.action.doAction("shopify_connector_inwi.shopify_refunds_action");
    }
    
}

// Helper function to poll for the canvas element  
async function getCanvasElement(instanceId) {
    let attempts = 0;
    let element;
    while (attempts < 10) { // Increased attempts for better reliability
        element = document.getElementById(`shopify_chart_${instanceId}`);
        if (element) return element;
        await new Promise(resolve => setTimeout(resolve, 100)); // Wait longer
        attempts++;
    }
    console.error(`Chart element shopify_chart_${instanceId} not found after retries.`);
    return null;
}


registry.category("actions").add("shopify_conector.ShopifyClientAction", ShopifyClientAction);
