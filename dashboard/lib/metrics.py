"""
Prometheus metrics endpoint for monitoring.
Exposes metrics at /metrics for Prometheus scraping.
"""

from datetime import datetime, timezone
from typing import Optional


def format_prometheus_metrics(status: dict) -> str:
    """
    Format status as Prometheus-compatible metrics.
    
    Args:
        status: Output from gather_status()
        
    Returns:
        Prometheus text format metrics
    """
    lines = []
    
    # Help and type declarations
    lines.append("# HELP auto_company_loop_running Whether the auto loop is running (1=running, 0=stopped)")
    lines.append("# TYPE auto_company_loop_running gauge")
    
    lines.append("# HELP auto_company_loop_count Total number of cycles completed")
    lines.append("# TYPE auto_company_loop_count counter")
    
    lines.append("# HELP auto_company_error_count Number of consecutive errors")
    lines.append("# TYPE auto_company_error_count gauge")
    
    lines.append("# HELP auto_company_agent_activity_total Total agent activities recorded")
    lines.append("# TYPE auto_company_agent_activity_total counter")
    
    lines.append("# HELP auto_company_info Build and version information")
    lines.append("# TYPE auto_company_info gauge")
    
    # Loop metrics
    loop_running = 1 if status.get("loop", {}).get("running", False) else 0
    lines.append(f'auto_company_loop_running{{engine="{status.get("engine", {}).get("active", "unknown")}"}} {loop_running}')
    
    loop_count = status.get("loop", {}).get("loopCount", "0")
    try:
        loop_count = int(loop_count)
    except (ValueError, TypeError):
        loop_count = 0
    lines.append(f'auto_company_loop_count{{engine="{status.get("engine", {}).get("active", "unknown")}"}} {loop_count}')
    
    error_count = status.get("loop", {}).get("errorCount", "0")
    try:
        error_count = int(error_count)
    except (ValueError, TypeError):
        error_count = 0
    lines.append(f'auto_company_error_count{{engine="{status.get("engine", {}).get("active", "unknown")}"}} {error_count}')
    
    # Agent activity metrics
    agent_stats = status.get("agentStats", {})
    for agent, stats in agent_stats.items():
        count = stats.get("count", 0)
        role = stats.get("role", "unknown")
        lines.append(f'auto_company_agent_activity_total{{agent="{agent}",role="{role}"}} {count}')
    
    # Info gauge (always 1, used for labels)
    model = status.get("loop", {}).get("model", "unknown")
    engine = status.get("engine", {}).get("active", "unknown")
    lines.append(f'auto_company_info{{engine="{engine}",model="{model}"}} 1')
    
    return "\n".join(lines) + "\n"