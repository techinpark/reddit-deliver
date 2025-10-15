"""
Monitor CLI commands.

Handles monitor start operation in both single-run and daemon modes.
"""

from services.monitor import Monitor
from cli import print_success, print_error, print_info
from lib.logger import get_logger

logger = get_logger("cli.monitor")


def handle_monitor_start(args):
    """Start monitoring."""
    try:
        monitor = Monitor()

        if args.once:
            # Run single monitoring cycle
            print_info("Starting single monitoring cycle...")
            stats = monitor.run_once()

            print_success("Monitoring cycle complete", args.json, data=stats)
            print_info(f"Subreddits checked: {stats['total_checked']}")
            print_info(f"New posts processed: {stats['total_posts']}")
            if stats['errors'] > 0:
                print_info(f"Errors: {stats['errors']}")

        elif getattr(args, 'daemon', False):
            # Run in daemon mode (explicit flag)
            interval = getattr(args, 'interval', 300)
            print_info(f"Starting daemon mode (interval: {interval}s)...")
            print_info("Press Ctrl+C to stop")

            monitor.run_daemon(interval=interval)

        else:
            # Default behavior: run in daemon mode
            interval = getattr(args, 'interval', 300)
            print_info(f"Starting daemon mode (interval: {interval}s)...")
            print_info("Press Ctrl+C to stop")

            monitor.run_daemon(interval=interval)

    except KeyboardInterrupt:
        print_info("\nMonitoring stopped by user")
    except Exception as e:
        logger.error(f"Monitoring failed: {e}")
        print_error(f"Monitoring failed: {e}", args.json, exit_code=3)
