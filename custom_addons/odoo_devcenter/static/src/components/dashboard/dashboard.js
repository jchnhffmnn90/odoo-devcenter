/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
const { Component, useState, onWillStart, onWillUnmount } = owl;

export class DevCenterDashboard extends Component {
    setup() {
        this.rpc = useService("rpc");
        this.state = useState({
            metrics: null,
            loading: true
        });

        onWillStart(async () => {
            await this.fetchMetrics();
            this.interval = setInterval(() => this.fetchMetrics(), 2000);
        });

        onWillUnmount(() => {
            clearInterval(this.interval);
        });
    }

    async fetchMetrics() {
        try {
            const data = await this.rpc("/devcenter/metrics", {});
            this.state.metrics = data;
            this.state.loading = false;
        } catch (error) {
            console.error("Failed to fetch DevCenter metrics", error);
        }
    }
}

DevCenterDashboard.template = "odoo_devcenter.Dashboard";
registry.category("actions").add("devcenter_dashboard", DevCenterDashboard);
