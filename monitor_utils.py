import psutil
import os


def get_process_metrics(keyword):
    """
    Find processes containing keyword in their command line.
    Returns aggregated (cpu_percent, memory_mb, read_bytes, write_bytes).
    """
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
                # get CPU percent (non-blocking, might need two calls for accuracy but we'll take what's there)
                cpu = p.cpu_percent(interval=None)
                total_cpu += cpu

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

    return total_cpu, total_mem, read_bytes, write_bytes, open_files, connections


def get_system_metrics():
    return {"cpu": psutil.cpu_percent(), "ram": psutil.virtual_memory().percent}
