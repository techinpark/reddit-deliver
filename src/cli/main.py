"""
Main CLI entry point for reddit-deliver.

Provides command-line interface for Reddit monitoring and webhook delivery.
"""

import sys
import argparse
from lib.logger import setup_logger


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog='reddit-deliver',
        description='Reddit monitoring and webhook delivery system with translation'
    )

    parser.add_argument('--version', '-v', action='version', version='reddit-deliver 0.1.0')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    parser.add_argument('--verbose', action='store_true', help='Enable verbose logging')
    parser.add_argument('--config', help='Path to config file (default: config/config.yaml)')
    parser.add_argument('--db', help='Path to database file (default: data/reddit-deliver.db)')

    # Subcommands
    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Config commands (will be implemented in later tasks)
    config_parser = subparsers.add_parser('config', help='Manage configuration')
    config_subparsers = config_parser.add_subparsers(dest='config_command')
    config_subparsers.add_parser('init', help='Initialize configuration')
    config_set_parser = config_subparsers.add_parser('set', help='Set configuration value')
    config_set_parser.add_argument('key', help='Configuration key')
    config_set_parser.add_argument('value', help='Configuration value')
    config_get_parser = config_subparsers.add_parser('get', help='Get configuration value')
    config_get_parser.add_argument('key', help='Configuration key (or "all")')

    # Subreddit commands
    subreddit_parser = subparsers.add_parser('subreddit', help='Manage subreddits')
    subreddit_subparsers = subreddit_parser.add_subparsers(dest='subreddit_command')
    subreddit_add_parser = subreddit_subparsers.add_parser('add', help='Add subreddit')
    subreddit_add_parser.add_argument('name', help='Subreddit name')
    subreddit_add_parser.add_argument('--url', help='Subreddit URL (optional)')

    # Webhook commands
    webhook_parser = subparsers.add_parser('webhook', help='Manage webhooks')
    webhook_subparsers = webhook_parser.add_subparsers(dest='webhook_command')
    webhook_set_parser = webhook_subparsers.add_parser('set', help='Set webhook URL')
    webhook_set_parser.add_argument('type', choices=['discord', 'slack'], help='Webhook type')
    webhook_set_parser.add_argument('url', help='Webhook URL')

    # Monitor commands
    monitor_parser = subparsers.add_parser('monitor', help='Control monitoring')
    monitor_subparsers = monitor_parser.add_subparsers(dest='monitor_command')
    monitor_start_parser = monitor_subparsers.add_parser('start', help='Start monitoring')
    monitor_start_parser.add_argument('--once', action='store_true', help='Run once and exit')
    monitor_start_parser.add_argument('--daemon', action='store_true', help='Run as daemon')

    args = parser.parse_args()

    # Setup logging
    logger = setup_logger(verbose=args.verbose)

    # Handle no command
    if not args.command:
        parser.print_help()
        sys.exit(0)

    # Import command handlers
    from cli.config import handle_config_init, handle_config_set, handle_config_get
    from cli.subreddit import handle_subreddit_add
    from cli.webhook import handle_webhook_set, handle_webhook_test
    from cli.monitor_cmd import handle_monitor_start

    # Route to appropriate handler
    try:
        if args.command == 'config':
            if args.config_command == 'init':
                handle_config_init(args)
            elif args.config_command == 'set':
                handle_config_set(args)
            elif args.config_command == 'get':
                handle_config_get(args)
            else:
                config_parser.print_help()

        elif args.command == 'subreddit':
            if args.subreddit_command == 'add':
                handle_subreddit_add(args)
            else:
                subreddit_parser.print_help()

        elif args.command == 'webhook':
            if args.webhook_command == 'set':
                handle_webhook_set(args)
            elif args.webhook_command == 'test':
                handle_webhook_test(args)
            else:
                webhook_parser.print_help()

        elif args.command == 'monitor':
            if args.monitor_command == 'start':
                handle_monitor_start(args)
            else:
                monitor_parser.print_help()

        else:
            parser.print_help()

    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(130)
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        from cli import print_error
        print_error(f"Unexpected error: {e}", args.json if hasattr(args, 'json') else False, exit_code=1)


if __name__ == '__main__':
    main()
