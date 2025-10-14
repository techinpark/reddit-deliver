"""
CLI utilities for reddit-deliver.

Provides output formatters, error handlers, and common CLI functions.
"""

import sys
import json
from typing import Any, Dict, Optional


def print_success(message: str, json_output: bool = False, data: Optional[Dict[str, Any]] = None):
    """
    Print success message.

    Args:
        message: Success message
        json_output: Output as JSON
        data: Additional data to include in JSON output
    """
    if json_output:
        output = {"status": "success", "message": message}
        if data:
            output.update(data)
        print(json.dumps(output, indent=2))
    else:
        print(f"✓ {message}")


def print_error(message: str, json_output: bool = False, exit_code: int = 1):
    """
    Print error message and exit.

    Args:
        message: Error message
        json_output: Output as JSON
        exit_code: Exit code (0 = success, 1+ = error)
    """
    if json_output:
        output = {"status": "error", "message": message, "exit_code": exit_code}
        print(json.dumps(output, indent=2), file=sys.stderr)
    else:
        print(f"✗ Error: {message}", file=sys.stderr)

    sys.exit(exit_code)


def print_info(message: str, json_output: bool = False):
    """
    Print informational message.

    Args:
        message: Info message
        json_output: Output as JSON (skips info messages in JSON mode)
    """
    if not json_output:
        print(f"  {message}")


def format_table(headers: list, rows: list) -> str:
    """
    Format data as a simple table.

    Args:
        headers: List of column headers
        rows: List of rows (each row is a list of values)

    Returns:
        Formatted table string
    """
    if not rows:
        return "No data"

    # Calculate column widths
    col_widths = [len(str(h)) for h in headers]
    for row in rows:
        for i, cell in enumerate(row):
            col_widths[i] = max(col_widths[i], len(str(cell)))

    # Create separator line
    separator = "+-" + "-+-".join("-" * w for w in col_widths) + "-+"

    # Format header
    header = "| " + " | ".join(
        str(h).ljust(w) for h, w in zip(headers, col_widths)
    ) + " |"

    # Format rows
    formatted_rows = []
    for row in rows:
        formatted_row = "| " + " | ".join(
            str(cell).ljust(w) for cell, w in zip(row, col_widths)
        ) + " |"
        formatted_rows.append(formatted_row)

    # Combine
    return "\n".join([separator, header, separator] + formatted_rows + [separator])


def confirm(prompt: str, default: bool = False) -> bool:
    """
    Ask user for confirmation.

    Args:
        prompt: Confirmation prompt
        default: Default value if user presses enter

    Returns:
        True if confirmed, False otherwise
    """
    suffix = " [Y/n]" if default else " [y/N]"
    response = input(prompt + suffix + " ").strip().lower()

    if not response:
        return default

    return response in ('y', 'yes')
