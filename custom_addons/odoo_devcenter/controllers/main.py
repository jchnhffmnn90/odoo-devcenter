import psutil
from odoo import http
from odoo.http import request


def get_process_metrics(keyword):
    total_cpu = 0.0
    total_mem = 0.0
    read_bytes = 0
    write_bytes = 0
    open_files = 0
    connections = 0

    for p in psutil.process_iter(
        ["pid", "name", "cmdline", "cpu_percent", "memory_info", "io_counters"]
    ):
        try:
            cmdline = p.info.get("cmdline")
            if cmdline and any(keyword in arg for arg in cmdline):
                total_cpu += p.cpu_percent(interval=None)

                mem = p.info.get("memory_info")
                if mem:
                    total_mem += mem.rss / (1024 * 1024)

                io = p.info.get("io_counters")
                if io:
                    read_bytes += io.read_bytes
                    write_bytes += io.write_bytes

                try:
                    open_files += len(p.open_files())
                except (psutil.AccessDenied, psutil.Error, AttributeError):
                    pass

                try:
                    connections += len(p.connections())
                except (psutil.AccessDenied, psutil.Error, AttributeError):
                    pass
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

    return {
        "cpu": round(total_cpu, 1),
        "mem": round(total_mem, 1),
        "read_mb": round(read_bytes / (1024 * 1024), 1),
        "write_mb": round(write_bytes / (1024 * 1024), 1),
        "open_files": open_files,
        "connections": connections,
    }


class DevCenterController(http.Controller):
    @http.route("/devcenter/metrics", type="json", auth="user")
    def get_metrics(self):
        odoo_metrics = get_process_metrics("odoo-bin")
        pg_metrics = get_process_metrics("postgres")
        sys_cpu = psutil.cpu_percent()
        sys_ram = psutil.virtual_memory().percent

        return {
            "odoo": odoo_metrics,
            "postgres": pg_metrics,
            "system": {"cpu": sys_cpu, "ram": sys_ram},
        }
