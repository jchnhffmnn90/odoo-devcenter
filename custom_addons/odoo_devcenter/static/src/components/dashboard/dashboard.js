/** @odoo-module **/

import { registry } from "@web/core/registry";
import { useService } from "@web/core/utils/hooks";
const { Component, useState, onWillStart, onWillUnmount } = owl;

export class DevCenterDashboard extends Component {
    setup() {
        this.rpc = this.env.services.rpc;
        this.state = useState({
            activeTab: "metrics",
            metrics: null,
            loadingMetrics: true,
            logs: "",
            testModule: "shopify_odoo_connector",
            testing: false,
            testOutput: "",
            testReturnCode: null
        });

        onWillStart(async () => {
            await this.fetchMetrics();
            this.interval = setInterval(() => this.tick(), 2000);
        });

        onWillUnmount(() => {
            clearInterval(this.interval);
        });
    }

    tick() {
        if (this.state.activeTab === "metrics") {
            this.fetchMetrics();
        } else if (this.state.activeTab === "logs") {
            this.fetchLogs();
        }
    }
    
    changeTab(tab) {
        this.state.activeTab = tab;
        this.tick();
    }

    async fetchMetrics() {
        try {
            const data = await this.rpc("/devcenter/metrics", {});
            this.state.metrics = data;
            this.state.loadingMetrics = false;
        } catch (error) {
            console.error("Failed to fetch DevCenter metrics", error);
        }
    }
    
    async fetchLogs() {
        try {
            const data = await this.rpc("/devcenter/logs", { lines: 100 });
            this.state.logs = data.logs;
        } catch (error) {
            console.error("Failed to fetch logs", error);
        }
    }
    
    async runTests() {
        if (this.state.testing) return;
        this.state.testing = true;
        this.state.testOutput = "Running tests... Please wait (this may take up to 2 minutes).";
        
        try {
            const data = await this.rpc("/devcenter/run_tests", { module: this.state.testModule });
            this.state.testOutput = data.output;
            this.state.testReturnCode = data.returncode;
        } catch (error) {
            console.error("Failed to run tests", error);
            this.state.testOutput = "RPC Error while calling test runner.";
        } finally {
            this.state.testing = false;
        }
    }
}

DevCenterDashboard.template = "odoo_devcenter.Dashboard";
registry.category("actions").add("devcenter_dashboard", DevCenterDashboard);
