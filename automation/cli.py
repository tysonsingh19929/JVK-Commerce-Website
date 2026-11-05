"""
AESAS Command Line Interface (CLI)
Allows operators to list specialists, run single specialist agents,
or execute the full 360-degree autonomous audit swarm.
"""

import sys
import json
import argparse

# Ensure UTF-8 output on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from .core.orchestrator import orchestrator

console = Console()

def list_specialists():
    specialists = orchestrator.list_specialists()
    table = Table(title="JVK Commerce - 15 Specialist Automation Service Areas", header_style="bold cyan")
    table.add_column("Area #", style="dim", width=8, justify="center")
    table.add_column("Specialist Agent", style="bold green", width=32)
    table.add_column("Preferred Engine", style="magenta", width=18)
    table.add_column("Operational Focus", style="white")

    for s in specialists:
        table.add_row(
            str(s["id"]),
            s["name"],
            s["preferred_engine"].upper(),
            s["description"]
        )
    console.print(table)

def run_single_agent(agent_id: int):
    console.print(f"[bold cyan]Launching Specialist Agent #{agent_id}...[/bold cyan]")
    res = orchestrator.run_agent(agent_id)
    
    if res.get("status") == "success":
        console.print(Panel(
            json.dumps(res, indent=2),
            title=f"[bold green][SUCCESS] {res.get('agent_name')} Completed in {res.get('duration_seconds')}s[/bold green]",
            border_style="green"
        ))
    else:
        console.print(Panel(
            f"Error: {res.get('error_message')}",
            title=f"[bold red][ERROR] {res.get('agent_name')} Failed[/bold red]",
            border_style="red"
        ))

def run_full_audit():
    console.print("[bold yellow]Initiating Complete 360-Degree Marketplace Agency Audit Swarm...[/bold yellow]")
    res = orchestrator.run_full_account_audit()
    console.print(Panel(
        f"Executed {res.get('modules_executed')} core specialist modules successfully.\nAudit logs saved to automation/data/",
        title="[bold green][SUCCESS] Full Account Audit Completed[/bold green]",
        border_style="green"
    ))

def main():
    parser = argparse.ArgumentParser(description="JVK Commerce Autonomous Specialist Automation CLI")
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    subparsers.add_parser("list", help="List all 15 specialist service areas")
    
    run_parser = subparsers.add_parser("run", help="Run a specific specialist agent")
    run_parser.add_argument("agent_id", type=int, help="Specialist Area ID (1 to 15)")

    subparsers.add_parser("audit", help="Run the full 360-degree account audit swarm")

    args = parser.parse_args()

    if args.command == "list" or not args.command:
        list_specialists()
    elif args.command == "run":
        run_single_agent(args.agent_id)
    elif args.command == "audit":
        run_full_audit()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
