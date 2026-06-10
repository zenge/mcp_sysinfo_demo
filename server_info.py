#!/usr/bin/env python3
"""
MCP Server Demo — 返回当前设备系统信息
启动: python3.14 server.py
"""

import json
import socket
import platform
from datetime import datetime

import psutil
from mcp.server.fastmcp import FastMCP

# ── 创建 MCP Server ──────────────────────────────────────────
mcp = FastMCP("sysinfo-server")


# ── Tool 1: 系统概览 ─────────────────────────────────────────
@mcp.tool()
def get_system_info() -> str:
    """获取当前设备系统概览（OS、主机名、架构、内核、Python版本、运行时间）"""
    boot = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot
    return json.dumps({
        "hostname": socket.gethostname(),
        "os": platform.system(),
        "os_version": platform.version(),
        "kernel": platform.release(),
        "architecture": platform.machine(),
        "python_version": platform.python_version(),
        "boot_time": boot.strftime("%Y-%m-%d %H:%M:%S"),
        "uptime": f"{uptime.days}天 {uptime.seconds // 3600}小时 {(uptime.seconds % 3600) // 60}分钟",
    }, ensure_ascii=False, indent=2)


# ── Tool 2: CPU 信息 ─────────────────────────────────────────
@mcp.tool()
def get_cpu_info() -> str:
    """获取 CPU 详细信息（型号、物理/逻辑核心数、频率、当前使用率）"""
    freq = psutil.cpu_freq()
    return json.dumps({
        "model": platform.processor() or "Apple Silicon",
        "physical_cores": psutil.cpu_count(logical=False),
        "logical_cores": psutil.cpu_count(logical=True),
        "current_freq_mhz": round(freq.current, 0) if freq else "N/A",
        "max_freq_mhz": round(freq.max, 0) if freq else "N/A",
        "usage_percent": psutil.cpu_percent(interval=0.5),
    }, ensure_ascii=False, indent=2)


# ── Tool 3: 内存信息 ─────────────────────────────────────────
@mcp.tool()
def get_memory_info() -> str:
    """获取内存和交换空间使用情况"""
    mem = psutil.virtual_memory()
    swap = psutil.swap_memory()
    return json.dumps({
        "total_gb": round(mem.total / (1024**3), 1),
        "available_gb": round(mem.available / (1024**3), 1),
        "used_gb": round(mem.used / (1024**3), 1),
        "percent_used": mem.percent,
        "swap_total_gb": round(swap.total / (1024**3), 1),
        "swap_used_gb": round(swap.used / (1024**3), 1),
        "swap_percent": swap.percent,
    }, ensure_ascii=False, indent=2)


# ── Tool 4: 磁盘信息 ─────────────────────────────────────────
@mcp.tool()
def get_disk_info() -> str:
    """获取磁盘分区及使用情况"""
    partitions = []
    for part in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(part.mountpoint)
            partitions.append({
                "mountpoint": part.mountpoint,
                "filesystem": part.fstype,
                "total_gb": round(usage.total / (1024**3), 1),
                "used_gb": round(usage.used / (1024**3), 1),
                "free_gb": round(usage.free / (1024**3), 1),
                "percent_used": usage.percent,
            })
        except PermissionError:
            pass
    return json.dumps(partitions, ensure_ascii=False, indent=2)


# ── Tool 5: 网络信息 ─────────────────────────────────────────
@mcp.tool()
def get_network_info() -> str:
    """获取各网络接口的 IPv4 地址"""
    interfaces = {}
    for name, addrs in psutil.net_if_addrs().items():
        if_addrs = []
        for addr in addrs:
            if addr.family == socket.AF_INET:
                if_addrs.append({"ip": addr.address, "netmask": addr.netmask})
        if if_addrs:
            interfaces[name] = if_addrs
    return json.dumps(interfaces, ensure_ascii=False, indent=2)


# ── 启动 ─────────────────────────────────────────────────────
if __name__ == "__main__":
    mcp.run()
