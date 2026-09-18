import os
import asyncio
from pathlib import Path
from textual.app import App, ComposeResult
from textual.containers import Container, Horizontal, Vertical
from textual.widgets import (
    Header,
    Footer,
    TabbedContent,
    TabPane,
    Static,
    Log,
    Button,
    Label,
    DataTable,
)
from textual.reactive import reactive

from monitor_utils import get_process_metrics, get_system_metrics

BASE_DIR = Path(__file__).resolve().parent
LOG_FILE = BASE_DIR / "odoo.log"


class MetricWidget(Static):
    value = reactive("Loading...")

    def __init__(self, title, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title_text = title

    def render(self):
        return f"[b]{self.title_text}[/b]\n{self.value}"


class Dashboard(Container):
    def compose(self) -> ComposeResult:
        with Horizontal():
            with Vertical(classes="column"):
                yield Label("[b]Odoo Process[/b]", classes="section-title")
                yield MetricWidget("CPU", id="odoo_cpu")
                yield MetricWidget("RAM (MB)", id="odoo_ram")
                yield MetricWidget("Disk IO (R/W MB)", id="odoo_io")
                yield MetricWidget("Open Files/Conns", id="odoo_files")
                yield Button("Restart Server", id="restart_server", variant="warning")
            with Vertical(classes="column"):
                yield Label("[b]PostgreSQL Process[/b]", classes="section-title")
                yield MetricWidget("CPU", id="pg_cpu")
                yield MetricWidget("RAM (MB)", id="pg_ram")
                yield MetricWidget("Disk IO (R/W MB)", id="pg_io")
                yield MetricWidget("Open Files/Conns", id="pg_files")
            with Vertical(classes="column"):
                yield Label("[b]System[/b]", classes="section-title")
                yield MetricWidget("System CPU", id="sys_cpu")
                yield MetricWidget("System RAM", id="sys_ram")

    def on_mount(self) -> None:
        self.update_metrics()
        self.set_interval(2.0, self.update_metrics)

    def update_metrics(self) -> None:
        odoo_cpu, odoo_ram, odoo_r, odoo_w, odoo_f, odoo_c = get_process_metrics(
            "odoo-bin"
        )
        pg_cpu, pg_ram, pg_r, pg_w, pg_f, pg_c = get_process_metrics("postgres")
        sys_metrics = get_system_metrics()

        self.query_one("#odoo_cpu").value = f"{odoo_cpu:.1f} %"
        self.query_one("#odoo_ram").value = f"{odoo_ram:.1f} MB"
        self.query_one(
            "#odoo_io"
        ).value = f"{odoo_r / (1024 * 1024):.1f} / {odoo_w / (1024 * 1024):.1f}"
        self.query_one("#odoo_files").value = f"{odoo_f} / {odoo_c}"

        self.query_one("#pg_cpu").value = f"{pg_cpu:.1f} %"
        self.query_one("#pg_ram").value = f"{pg_ram:.1f} MB"
        self.query_one(
            "#pg_io"
        ).value = f"{pg_r / (1024 * 1024):.1f} / {pg_w / (1024 * 1024):.1f}"
        self.query_one("#pg_files").value = f"{pg_f} / {pg_c}"

        self.query_one("#sys_cpu").value = f"{sys_metrics['cpu']:.1f} %"
        self.query_one("#sys_ram").value = f"{sys_metrics['ram']:.1f} %"

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "restart_server":
            self.app.notify("Restarting Server...")
            self.run_worker(self.restart_server(), thread=True)

    def restart_server(self):
        import subprocess

        subprocess.run([f"{BASE_DIR}/stop.sh"])
        subprocess.run([f"{BASE_DIR}/start_bg.sh"])
        self.app.call_from_thread(self.app.notify, "Server Restarted!")


class LogViewer(Container):
    def compose(self) -> ComposeResult:
        self.log_widget = Log(highlight=True)
        yield self.log_widget

    def on_mount(self) -> None:
        self.run_worker(self.tail_log(), thread=True)

    def tail_log(self):
        if not LOG_FILE.exists():
            self.app.call_from_thread(
                self.log_widget.write_line, f"Log file not found: {LOG_FILE}"
            )
            return

        with open(LOG_FILE, "r") as f:
            # Go to the end of file minus some bytes to show last lines
            f.seek(0, 2)
            if f.tell() > 2000:
                f.seek(f.tell() - 2000, 0)
            else:
                f.seek(0, 0)

            while True:
                line = f.readline()
                if line:
                    self.app.call_from_thread(
                        self.log_widget.write_line, line.strip("\n")
                    )
                else:
                    import time

                    time.sleep(0.5)


class TestRunner(Container):
    def compose(self) -> ComposeResult:
        yield Button(
            "Run Tests for shopify_odoo_connector", id="run_tests", variant="primary"
        )
        self.test_output = Log(highlight=True, id="test_log")
        yield self.test_output

    async def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "run_tests":
            self.test_output.clear()
            self.test_output.write_line("Starting tests...")
            self.run_worker(self.execute_tests(), thread=True)

    def execute_tests(self):
        import subprocess

        cmd = [
            f"{BASE_DIR}/venv/bin/python",
            f"{BASE_DIR}/odoo-19.0/odoo-bin",
            "-c",
            f"{BASE_DIR}/odoo.conf",
            "--test-enable",
            "-i",
            "shopify_odoo_connector",
            "--stop-after-init",
        ]

        process = subprocess.Popen(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        for line in iter(process.stdout.readline, ""):
            self.app.call_from_thread(self.test_output.write_line, line.strip())
        process.stdout.close()
        process.wait()
        self.app.call_from_thread(
            self.test_output.write_line,
            f"--- Tests finished with code {process.returncode} ---",
        )


class OdooDevCenter(App):
    CSS = """
    Screen {
        layout: vertical;
    }
    
    TabbedContent {
        height: 1fr;
    }

    Dashboard {
        height: 1fr;
        padding: 1;
    }
    
    .column {
        width: 1fr;
        height: 1fr;
        border: solid green;
        padding: 1;
        margin: 1;
    }
    
    .section-title {
        content-align: center middle;
        width: 100%;
        margin-bottom: 1;
        background: $boost;
    }

    MetricWidget {
        height: 4;
        content-align: center middle;
        border: round #666;
        margin-bottom: 1;
    }
    
    LogViewer {
        height: 1fr;
    }
    
    TestRunner {
        height: 1fr;
        padding: 1;
    }
    
    #test_log {
        margin-top: 1;
        border: solid white;
        height: 1fr;
    }
    """

    BINDINGS = [
        ("q", "quit", "Quit"),
        ("d", "toggle_dark", "Toggle Dark Mode"),
    ]

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with TabbedContent():
            with TabPane("Dashboard", id="tab-dashboard"):
                yield Dashboard()
            with TabPane("Logs", id="tab-logs"):
                yield LogViewer()
            with TabPane("Tests", id="tab-tests"):
                yield TestRunner()
        yield Footer()


if __name__ == "__main__":
    app = OdooDevCenter()
    app.run()
