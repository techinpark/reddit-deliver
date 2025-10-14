"""
Monitor CLI commands.

Handles monitor start --once operation (MVP version).
"""

from services.monitor import Monitor
from cli import print_success, print_error, print_info
from lib.logger import get_logger

logger = get_logger("cli.monitor")


def handle_monitor_start(args):
    """Start monitoring."""
    if not args.once:
        print_error(
            "Daemon mode not yet implemented. Use --once to run single check cycle.",
            args.json,
            exit_code=1
        )

    # Run single monitoring cycle
    print_info("Starting single monitoring cycle...")

    try:
        monitor = Monitor()
        stats = monitor.run_once()

        print_success("Monitoring cycle complete", args.json, data=stats)
        print_info(f"Subreddits checked: {stats['total_checked']}")
        print_info(f"New posts processed: {stats['total_posts']}")
        if stats['errors'] > 0:
            print_info(f"Errors: {stats['errors']}")

    except Exception as e:
        logger.error(f"Monitoring failed: {e}")
        print_error(f"Monitoring failed: {e}", args.json, exit_code=3)
