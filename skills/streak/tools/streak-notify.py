#!/usr/bin/env python3
"""
Streak Notification Script

Checks for due/overdue streak challenges and sends Telegram notifications.
Run via cron, systemd timer, or GitHub Actions.

Setup:
1. Create a Telegram bot via @BotFather
2. Get your chat ID via @userinfobot
3. Add credentials to .streak/config.md
4. Schedule this script to run daily

Usage:
    python streak-notify.py [path/to/.streak]

    # Or from project root:
    python .streak/tools/streak-notify.py
"""

import os
import re
import sys
import json
import urllib.request
import urllib.error
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any


def parse_markdown_field(content: str, field: str) -> Optional[str]:
    """Extract a **Field:** value from markdown content."""
    pattern = rf'\*\*{re.escape(field)}:\*\*\s*(.+?)(?:\n|$)'
    match = re.search(pattern, content, re.IGNORECASE)
    return match.group(1).strip() if match else None


def parse_date(date_str: str) -> Optional[datetime]:
    """Parse a date string in various formats."""
    formats = ['%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y', '%d/%m/%Y']
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    return None


def parse_cadence(cadence_str: str) -> int:
    """Convert cadence string to days. Returns interval in days."""
    cadence = cadence_str.lower().strip()

    if 'daily' in cadence:
        return 1
    elif 'weekly' in cadence:
        return 7
    elif 'every' in cadence:
        # Parse "Every X days" or "Every 2 days"
        match = re.search(r'every\s+(\d+)\s*(?:day|days)?', cadence)
        if match:
            return int(match.group(1))

    # Default to daily if can't parse
    return 1


def load_config(streak_path: Path) -> Dict[str, Any]:
    """Load notification config from .streak/config.md"""
    config_file = streak_path / 'config.md'
    config = {
        'telegram_bot_token': None,
        'telegram_chat_id': None,
        'notification_time': '09:00',
        'notifications_enabled': True,
    }

    if not config_file.exists():
        return config

    content = config_file.read_text()

    # Parse Telegram settings
    config['telegram_bot_token'] = parse_markdown_field(content, 'Telegram Bot Token')
    config['telegram_chat_id'] = parse_markdown_field(content, 'Telegram Chat ID')

    enabled = parse_markdown_field(content, 'Notifications')
    if enabled:
        config['notifications_enabled'] = enabled.lower() in ['enabled', 'true', 'yes', 'on']

    return config


def get_challenge_status(challenge_path: Path) -> Optional[Dict[str, Any]]:
    """Get status info for a single challenge."""
    config_file = challenge_path / 'challenge-config.md'

    if not config_file.exists():
        return None

    content = config_file.read_text()

    # Parse challenge info
    name = parse_markdown_field(content, 'Name')
    status = parse_markdown_field(content, 'Status')
    cadence = parse_markdown_field(content, 'Cadence')
    check_ins = parse_markdown_field(content, 'Check-ins')
    last_checkin = parse_markdown_field(content, 'Last Check-in')
    goal = parse_markdown_field(content, 'Goal')
    streak = parse_markdown_field(content, 'Current Streak')

    # Skip non-active challenges
    if status and status.lower() not in ['active']:
        return None

    if not name or not cadence:
        return None

    # Calculate days since last check-in
    cadence_days = parse_cadence(cadence)

    if last_checkin:
        last_date = parse_date(last_checkin)
        if last_date:
            days_since = (datetime.now() - last_date).days
        else:
            days_since = 0
    else:
        # No check-ins yet, use start date
        started = parse_markdown_field(content, 'Started')
        if started:
            start_date = parse_date(started)
            days_since = (datetime.now() - start_date).days if start_date else 0
        else:
            days_since = 0

    # Determine notification status
    if days_since >= cadence_days:
        if days_since > cadence_days:
            notify_status = 'overdue'
        else:
            notify_status = 'due'
    else:
        notify_status = 'ok'

    return {
        'name': name,
        'goal': goal,
        'cadence_days': cadence_days,
        'days_since': days_since,
        'status': notify_status,
        'streak': streak or '0',
        'check_ins': check_ins or '0',
    }


def get_all_challenges(streak_path: Path) -> List[Dict[str, Any]]:
    """Get status for all active challenges."""
    challenges_dir = streak_path / 'challenges'

    if not challenges_dir.exists():
        return []

    challenges = []
    for challenge_dir in challenges_dir.iterdir():
        if challenge_dir.is_dir():
            status = get_challenge_status(challenge_dir)
            if status:
                challenges.append(status)

    return challenges


def send_telegram_message(token: str, chat_id: str, message: str) -> bool:
    """Send a message via Telegram Bot API."""
    url = f'https://api.telegram.org/bot{token}/sendMessage'

    data = json.dumps({
        'chat_id': chat_id,
        'text': message,
        'parse_mode': 'Markdown',
    }).encode('utf-8')

    headers = {'Content-Type': 'application/json'}

    try:
        req = urllib.request.Request(url, data=data, headers=headers)
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.status == 200
    except urllib.error.URLError as e:
        print(f"Error sending Telegram message: {e}")
        return False


def format_notification(challenges: List[Dict[str, Any]]) -> Optional[str]:
    """Format notification message for due/overdue challenges."""
    due = [c for c in challenges if c['status'] == 'due']
    overdue = [c for c in challenges if c['status'] == 'overdue']

    if not due and not overdue:
        return None

    lines = ["*Streak Check-in Reminder*\n"]

    if overdue:
        lines.append("*Overdue:*")
        for c in overdue:
            days = c['days_since'] - c['cadence_days']
            lines.append(f"  {c['name']} ({days}d overdue, streak: {c['streak']})")
        lines.append("")

    if due:
        lines.append("*Due Today:*")
        for c in due:
            lines.append(f"  {c['name']} (streak: {c['streak']})")
        lines.append("")

    lines.append("_Open Claude Code and say: check in_")

    return '\n'.join(lines)


def find_streak_path() -> Optional[Path]:
    """Find .streak directory, searching upward from cwd."""
    current = Path.cwd()

    # Check if path provided as argument
    if len(sys.argv) > 1:
        arg_path = Path(sys.argv[1])
        if arg_path.exists():
            if arg_path.name == '.streak':
                return arg_path
            elif (arg_path / '.streak').exists():
                return arg_path / '.streak'

    # Search upward from current directory
    for parent in [current] + list(current.parents):
        streak_path = parent / '.streak'
        if streak_path.exists():
            return streak_path

    return None


def main():
    """Main entry point."""
    # Find .streak directory
    streak_path = find_streak_path()

    if not streak_path:
        print("Error: .streak directory not found")
        print("Usage: python streak-notify.py [path/to/.streak]")
        sys.exit(1)

    print(f"Using streak path: {streak_path}")

    # Load config
    config = load_config(streak_path)

    if not config['notifications_enabled']:
        print("Notifications disabled in config")
        sys.exit(0)

    if not config['telegram_bot_token'] or not config['telegram_chat_id']:
        print("Error: Telegram credentials not configured")
        print("Add to .streak/config.md:")
        print("  **Telegram Bot Token:** your-bot-token")
        print("  **Telegram Chat ID:** your-chat-id")
        sys.exit(1)

    # Get challenge statuses
    challenges = get_all_challenges(streak_path)

    if not challenges:
        print("No active challenges found")
        sys.exit(0)

    # Format and send notification
    message = format_notification(challenges)

    if message:
        print("Sending notification...")
        print(message)
        print()

        success = send_telegram_message(
            config['telegram_bot_token'],
            config['telegram_chat_id'],
            message
        )

        if success:
            print("Notification sent!")
        else:
            print("Failed to send notification")
            sys.exit(1)
    else:
        print("All challenges on track - no notification needed")
        # Print status anyway
        for c in challenges:
            days_left = c['cadence_days'] - c['days_since']
            print(f"  {c['name']}: {days_left}d until due")


if __name__ == '__main__':
    main()
