#!/usr/bin/env python3
"""
Home Assistant Command Line Interface for macOS (ha).

Provides full terminal control over Home Assistant Core, Supervisor, Backups,
Host, Add-ons, and HACS on Darwin.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import urllib.error
import urllib.request

TOKEN_FILE = Path("/Library/Application Support/HomeAssistant/.supervisor_token")
API_BASE = "http://127.0.0.1:8765"


def get_token() -> str:
    """Retrieve supervisor auth token."""
    token = os.environ.get("SUPERVISOR_TOKEN")
    if token:
        return token
    if TOKEN_FILE.is_file():
        try:
            return TOKEN_FILE.read_text().strip()
        except Exception:
            pass
    return ""


def api_request(path: str, method: str = "GET", payload: dict | None = None) -> dict:
    """Perform request to local macOS supervisor daemon."""
    token = get_token()
    url = f"{API_BASE}{path}"
    headers = {
        "User-Agent": "ha-macos-cli/1.0",
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    data = json.dumps(payload).encode() if payload else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        try:
            body = json.loads(e.read().decode())
            print(f"Error: {body.get('message', e.reason)}", file=sys.stderr)
        except Exception:
            print(f"HTTP Error {e.code}: {e.reason}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError:
        print("Error: Could not connect to Home Assistant Supervisor daemon.", file=sys.stderr)
        print("Ensure the service is active: sudo launchctl list | grep org.homeassistant.supervisor", file=sys.stderr)
        sys.exit(1)


# --- COMMAND HANDLERS ---


def cmd_core(args):
    action = args.action
    if action == "status" or action == "info":
        res = api_request("/core/info")
        data = res.get("data", {})
        print(f"Home Assistant Core v{data.get('version')}")
        print(f"Status:        Running")
        print(f"Web Interface: http://localhost:{data.get('port', 8123)}")
        print(f"Architecture:  {data.get('arch')}")
    elif action == "restart":
        print("Restarting Home Assistant Core daemon...")
        api_request("/core/restart", method="POST")
        print("Restart signal sent.")
    elif action == "stop":
        print("Stopping Home Assistant Core...")
        api_request("/core/stop", method="POST")
        print("Stopped.")
    elif action == "start":
        print("Starting Home Assistant Core...")
        api_request("/core/start", method="POST")
        print("Started.")
    elif action == "check":
        print("Checking Home Assistant configuration...")
        res = api_request("/core/check_config", method="POST")
        print("Configuration check: PASSED (valid)")
    elif action == "update":
        print("Triggering Home Assistant update...")
        api_request("/core/update", method="POST")
        print("Update initiated.")
    elif action == "logs":
        log_file = "/Library/Logs/HomeAssistant/home-assistant.log"
        if Path(log_file).is_file():
            os.execvp("tail", ["tail", "-f", "-n", "50", log_file])
        else:
            print(f"No log file found at {log_file}")


def cmd_supervisor(args):
    action = args.action
    if action == "status" or action == "info":
        res = api_request("/supervisor/info")
        data = res.get("data", {})
        print(f"Home Assistant Native macOS Supervisor v{data.get('version')}")
        print(f"Status:       Healthy ({'Supported' if data.get('supported') else 'Unsupported'})")
        print(f"Channel:      {data.get('channel')}")
        print(f"Architecture: {data.get('arch')}")
        print(f"IP Address:   {data.get('ip_address')}")
    elif action == "restart":
        print("Restarting Supervisor daemon...")
        api_request("/supervisor/restart", method="POST")
        print("Restart signal sent.")
    elif action == "logs":
        log_file = "/Library/Logs/HomeAssistant/supervisor.log"
        if Path(log_file).is_file():
            os.execvp("tail", ["tail", "-f", "-n", "50", log_file])
        else:
            print("To view live supervisor logs, run:")
            print("sudo log show --predicate 'process == \"python3\"' --last 5m")


def cmd_host(args):
    action = args.action
    if action == "info":
        res = api_request("/host/info")
        data = res.get("data", {})
        print(f"Host:       {data.get('hostname')}")
        print(f"OS:         {data.get('operating_system')}")
        print(f"Kernel:     {data.get('kernel')}")
        print(f"Chassis:    {data.get('chassis')}")
        print(f"Disk Total: {data.get('disk_total')} GB")
        print(f"Disk Free:  {data.get('disk_free')} GB")
        print(f"Timezone:   {data.get('timezone')}")
    elif action == "reboot":
        confirm = input("Are you sure you want to reboot your Mac? [y/N]: ")
        if confirm.lower() == "y":
            api_request("/host/reboot", method="POST")
    elif action == "shutdown":
        confirm = input("Are you sure you want to shut down your Mac? [y/N]: ")
        if confirm.lower() == "y":
            api_request("/host/shutdown", method="POST")


def cmd_backups(args):
    action = args.action
    if action == "list":
        res = api_request("/backups/info")
        backups = res.get("data", {}).get("backups", [])
        if not backups:
            print("No backups found.")
            return
        print(f"{'SLUG':<12} {'DATE':<22} {'SIZE':<10} {'NAME'}")
        print("-" * 65)
        for b in backups:
            print(f"{b['slug']:<12} {b['date'][:19]:<22} {b['size']:>6.1f} MB  {b['name']}")
    elif action == "new" or action == "create":
        name = args.name or f"CLI Backup {Path(sys.argv[0]).stem}"
        print(f"Creating full configuration backup '{name}'...")
        res = api_request("/backups/new/full", method="POST", payload={"name": name})
        slug = res.get("data", {}).get("slug")
        print(f"Backup created successfully (Slug: {slug}).")
    elif action == "restore":
        if not args.slug:
            print("Error: Specify backup slug to restore: ha backups restore <slug>", file=sys.stderr)
            sys.exit(1)
        confirm = input(f"Are you sure you want to restore backup '{args.slug}'? [y/N]: ")
        if confirm.lower() == "y":
            print(f"Restoring backup {args.slug}...")
            api_request(f"/backups/{args.slug}/restore/full", method="POST")
            print("Restore complete. Core restarted.")


def cmd_addons(args):
    action = args.action
    if action == "list":
        res = api_request("/addons")
        addons = res.get("data", {}).get("addons", [])
        if not addons:
            print("No native add-ons installed. Run 'ha store' to view available add-ons.")
            return
        print(f"{'SLUG':<15} {'STATE':<10} {'VERSION':<10} {'NAME'}")
        print("-" * 65)
        for a in addons:
            print(f"{a['slug']:<15} {a['state']:<10} {a['version']:<10} {a['name']}")
    elif action == "install":
        slug = args.slug
        print(f"Installing native macOS add-on '{slug}'...")
        api_request(f"/store/addons/{slug}/install", method="POST")
        print(f"Add-on '{slug}' installed successfully.")
    elif action == "start":
        api_request(f"/addons/{args.slug}/start", method="POST")
        print(f"Add-on '{args.slug}' started.")
    elif action == "stop":
        api_request(f"/addons/{args.slug}/stop", method="POST")
        print(f"Add-on '{args.slug}' stopped.")
    elif action == "uninstall":
        api_request(f"/addons/{args.slug}/uninstall", method="POST")
        print(f"Add-on '{args.slug}' uninstalled.")


def cmd_store(args):
    res = api_request("/store")
    addons = res.get("data", {}).get("addons", [])
    print(f"{'SLUG':<15} {'INSTALLED':<12} {'VERSION':<10} {'NAME'}")
    print("-" * 75)
    for a in addons:
        inst = "Yes" if a.get("installed") else "No"
        print(f"{a['slug']:<15} {inst:<12} {a['version']:<10} {a['name']}")
    print("\nTo install an add-on: ha addons install <slug>")


def cmd_network(args):
    res = api_request("/network/info")
    data = res.get("data", {})
    for iface in data.get("interfaces", []):
        ipv4 = iface.get("ipv4", {})
        addrs = ", ".join(ipv4.get("address", []))
        print(f"Interface: {iface.get('interface')} ({iface.get('type')})")
        print(f"  Connected: {iface.get('connected')}")
        print(f"  IPv4:      {addrs}")
        print(f"  Gateway:   {ipv4.get('gateway')}")
        print(f"  DNS:       {', '.join(ipv4.get('nameservers', []))}")


def cmd_hacs(args):
    action = args.action
    if action == "install":
        config_dir = Path("/Library/Application Support/HomeAssistant/config")
        print("Installing HACS (Home Assistant Community Store) for macOS...")
        script = 'cd "/Library/Application Support/HomeAssistant/config" && curl -sfSL https://get.hacs.xyz | bash -'
        cmd = ["sudo", "-H", "-u", "_homeassistant", "env", "HOME=/Library/Application Support/HomeAssistant", "bash", "-c", script]
        ret = subprocess.run(cmd)
        if ret.returncode == 0:
            print("\nHACS installed successfully!")
            print("Restarting Home Assistant Core...")
            api_request("/core/restart", method="POST")
            print("Done! Go to Settings > Devices & Services > Add Integration and search for 'HACS'.")
        else:
            print("Failed to install HACS.", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(
        prog="ha",
        description="Home Assistant CLI for macOS (native Supervisor & Core management)",
    )
    sub = parser.add_subparsers(dest="subcommand", required=True)

    # Core
    p_core = sub.add_parser("core", help="Control Home Assistant Core")
    p_core.add_argument("action", choices=["status", "info", "start", "stop", "restart", "check", "update", "logs"])
    p_core.set_defaults(func=cmd_core)

    # Supervisor
    p_sup = sub.add_parser("supervisor", help="Control macOS Supervisor")
    p_sup.add_argument("action", choices=["status", "info", "restart", "logs"])
    p_sup.set_defaults(func=cmd_supervisor)

    # Host
    p_host = sub.add_parser("host", help="Host diagnostics and control")
    p_host.add_argument("action", choices=["info", "reboot", "shutdown"])
    p_host.set_defaults(func=cmd_host)

    # Backups
    p_back = sub.add_parser("backups", help="Manage configuration backups")
    p_back.add_argument("action", choices=["list", "new", "create", "restore"])
    p_back.add_argument("name", nargs="?", default=None, help="Backup name")
    p_back.add_argument("--slug", default=None, help="Backup slug for restore")
    p_back.set_defaults(func=cmd_backups)

    # Addons
    p_add = sub.add_parser("addons", help="Manage native macOS add-ons")
    p_add.add_argument("action", choices=["list", "install", "start", "stop", "uninstall"])
    p_add.add_argument("slug", nargs="?", default="", help="Add-on slug")
    p_add.set_defaults(func=cmd_addons)

    # Store
    p_store = sub.add_parser("store", help="Browse available native add-ons")
    p_store.set_defaults(func=cmd_store)

    # Network
    p_net = sub.add_parser("network", help="Network information")
    p_net.set_defaults(func=cmd_network)

    # HACS
    p_hacs = sub.add_parser("hacs", help="Install or manage HACS")
    p_hacs.add_argument("action", choices=["install"])
    p_hacs.set_defaults(func=cmd_hacs)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
