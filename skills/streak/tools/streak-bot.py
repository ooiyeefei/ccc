#!/usr/bin/env python3
"""
Streak Telegram Bot - Interactive challenge tracking via Telegram.

Mirrors all Claude Code streak skill commands with a mobile-friendly UI.
Uses GitHub as source of truth - syncs via git pull/push.

Commands:
    /start      - Welcome message with main menu
    /streak     - Check in to active challenge
    /list       - List all challenges
    /stats      - View statistics for active challenge
    /insights   - Cross-challenge insights
    /new        - Create new challenge (guided)
    /switch     - Switch active challenge

Environment Variables:
    TELEGRAM_BOT_TOKEN  - Bot token from @BotFather (required)
    STREAK_PATH         - Path to .streak directory (default: ./.streak)
    GIT_AUTO_SYNC       - Enable git pull/push (default: true)
    ALLOWED_USERS       - Comma-separated chat IDs (required for notifications)
    NOTIFICATION_ENABLED - Enable daily push notifications (default: true)
    NOTIFICATION_HOUR   - Hour to send notification, 0-23 (default: 9)
    NOTIFICATION_MINUTE - Minute to send notification, 0-59 (default: 0)
    TIMEZONE            - Timezone for notifications (default: UTC, e.g., Asia/Singapore)

Docker:
    docker-compose up -d

Author: Claude Code Streak Skill
License: MIT
"""

import os
import re
import logging
import subprocess
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, List, Any

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# Logging setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
STREAK_PATH = Path(os.getenv('STREAK_PATH', './.streak'))
GIT_AUTO_SYNC = os.getenv('GIT_AUTO_SYNC', 'true').lower() == 'true'
ALLOWED_USERS = os.getenv('ALLOWED_USERS', '').split(',') if os.getenv('ALLOWED_USERS') else []

# Notification settings
NOTIFICATION_ENABLED = os.getenv('NOTIFICATION_ENABLED', 'true').lower() == 'true'
NOTIFICATION_HOUR = int(os.getenv('NOTIFICATION_HOUR', '9'))  # Hour in 24h format (0-23)
NOTIFICATION_MINUTE = int(os.getenv('NOTIFICATION_MINUTE', '0'))  # Minute (0-59)
TIMEZONE = os.getenv('TIMEZONE', 'UTC')  # Timezone for notifications

# Conversation states
(
    CHECKIN_CONFIRM,
    CHECKIN_SUMMARY,
    CHECKIN_FEELING,
    CHECKIN_LEARNING,
    CHECKIN_NEXT,
    NEW_TYPE,
    NEW_NAME,
    NEW_GOAL,
    NEW_CADENCE,
    SWITCH_SELECT,
) = range(10)


# =============================================================================
# Utility Functions
# =============================================================================

def git_sync(pull: bool = True, push: bool = False, message: str = None) -> bool:
    """Sync with git repository."""
    if not GIT_AUTO_SYNC:
        return True

    try:
        repo_path = STREAK_PATH.parent

        if pull:
            subprocess.run(
                ['git', 'pull', '--rebase'],
                cwd=repo_path,
                capture_output=True,
                timeout=30
            )

        if push and message:
            subprocess.run(['git', 'add', '.streak/'], cwd=repo_path, capture_output=True)
            subprocess.run(
                ['git', 'commit', '-m', message],
                cwd=repo_path,
                capture_output=True
            )
            subprocess.run(['git', 'push'], cwd=repo_path, capture_output=True, timeout=30)

        return True
    except Exception as e:
        logger.error(f"Git sync failed: {e}")
        return False


def parse_markdown_field(content: str, field: str) -> Optional[str]:
    """Extract a **Field:** value from markdown content."""
    pattern = rf'\*\*{re.escape(field)}:\*\*\s*(.+?)(?:\n|$)'
    match = re.search(pattern, content, re.IGNORECASE)
    return match.group(1).strip() if match else None


def parse_date(date_str: str) -> Optional[datetime]:
    """Parse a date string."""
    formats = ['%Y-%m-%d', '%d-%m-%Y', '%m/%d/%Y']
    for fmt in formats:
        try:
            return datetime.strptime(date_str.strip(), fmt)
        except ValueError:
            continue
    return None


def parse_cadence(cadence_str: str) -> int:
    """Convert cadence string to days."""
    cadence = cadence_str.lower().strip()
    if 'daily' in cadence:
        return 1
    elif 'weekly' in cadence:
        return 7
    elif 'every' in cadence:
        match = re.search(r'every\s+(\d+)', cadence)
        if match:
            return int(match.group(1))
    return 1


def get_active_challenge() -> Optional[Dict[str, Any]]:
    """Get the currently active challenge."""
    git_sync(pull=True)

    # Find active challenge from config files
    challenges_dir = STREAK_PATH / 'challenges'
    if not challenges_dir.exists():
        return None

    for challenge_dir in challenges_dir.iterdir():
        if not challenge_dir.is_dir():
            continue

        config_file = challenge_dir / 'challenge-config.md'
        if not config_file.exists():
            continue

        content = config_file.read_text()
        status = parse_markdown_field(content, 'Status')

        if status and status.lower() == 'active':
            return load_challenge(challenge_dir)

    return None


def load_challenge(challenge_dir: Path) -> Optional[Dict[str, Any]]:
    """Load challenge data from directory."""
    config_file = challenge_dir / 'challenge-config.md'
    if not config_file.exists():
        return None

    content = config_file.read_text()

    # Parse fields
    name = parse_markdown_field(content, 'Name')
    goal = parse_markdown_field(content, 'Goal')
    challenge_type = parse_markdown_field(content, 'Type')
    cadence = parse_markdown_field(content, 'Cadence')
    status = parse_markdown_field(content, 'Status')
    check_ins = parse_markdown_field(content, 'Check-ins')
    streak = parse_markdown_field(content, 'Current Streak')
    longest_streak = parse_markdown_field(content, 'Longest Streak')
    last_checkin = parse_markdown_field(content, 'Last Check-in')
    started = parse_markdown_field(content, 'Started')

    # Calculate days since last check-in
    days_since = 0
    if last_checkin:
        last_date = parse_date(last_checkin)
        if last_date:
            days_since = (datetime.now() - last_date).days

    cadence_days = parse_cadence(cadence) if cadence else 1

    # Determine status
    if days_since >= cadence_days:
        check_status = 'overdue' if days_since > cadence_days else 'due'
    else:
        check_status = 'ok'

    return {
        'id': challenge_dir.name,
        'path': challenge_dir,
        'name': name or challenge_dir.name,
        'goal': goal,
        'type': challenge_type,
        'cadence': cadence,
        'cadence_days': cadence_days,
        'status': status,
        'check_status': check_status,
        'check_ins': int(check_ins) if check_ins else 0,
        'streak': streak or '0',
        'longest_streak': longest_streak or '0',
        'last_checkin': last_checkin,
        'days_since': days_since,
        'started': started,
    }


def get_all_challenges() -> List[Dict[str, Any]]:
    """Get all challenges."""
    git_sync(pull=True)

    challenges = []
    challenges_dir = STREAK_PATH / 'challenges'

    if not challenges_dir.exists():
        return challenges

    for challenge_dir in challenges_dir.iterdir():
        if challenge_dir.is_dir():
            challenge = load_challenge(challenge_dir)
            if challenge:
                challenges.append(challenge)

    return challenges


def save_checkin(challenge: Dict, summary: str, feeling: str, learning: str, next_steps: str) -> bool:
    """Save a check-in to the challenge files."""
    try:
        challenge_dir = challenge['path']
        config_file = challenge_dir / 'challenge-config.md'

        # Update check-in count and streak
        new_checkins = challenge['check_ins'] + 1

        # Calculate new streak
        if challenge['days_since'] <= challenge['cadence_days']:
            new_streak = int(challenge['streak'].split()[0]) + 1
        else:
            new_streak = 1

        longest = max(new_streak, int(challenge['longest_streak'].split()[0]))
        today = datetime.now().strftime('%Y-%m-%d')

        # Update config file
        content = config_file.read_text()

        # Update fields
        content = re.sub(
            r'\*\*Check-ins:\*\*\s*\d+',
            f'**Check-ins:** {new_checkins}',
            content
        )
        content = re.sub(
            r'\*\*Current Streak:\*\*\s*[\d\w\s]+',
            f'**Current Streak:** {new_streak} days',
            content
        )
        content = re.sub(
            r'\*\*Longest Streak:\*\*\s*[\d\w\s]+',
            f'**Longest Streak:** {longest} days',
            content
        )

        # Add or update Last Check-in
        if '**Last Check-in:**' in content:
            content = re.sub(
                r'\*\*Last Check-in:\*\*\s*[\d\-]+',
                f'**Last Check-in:** {today}',
                content
            )
        else:
            content = content.replace(
                '**Status:**',
                f'**Last Check-in:** {today}\n**Status:**'
            )

        config_file.write_text(content)

        # Create session folder and notes
        sessions_dir = challenge_dir / 'sessions'
        sessions_dir.mkdir(exist_ok=True)

        session_num = new_checkins
        session_dir = sessions_dir / f'session-{session_num:03d}'
        session_dir.mkdir(exist_ok=True)

        notes_content = f"""# Session {session_num} Notes

**Date:** {today}
**Challenge:** {challenge['name']}
**Via:** Telegram Bot

---

## Summary
{summary}

---

## How It Went
{feeling}

---

## Key Learning
{learning}

---

## Next Steps
{next_steps}
"""

        (session_dir / 'notes.md').write_text(notes_content)

        # Update challenge log
        log_file = challenge_dir / 'challenge-log.md'
        if log_file.exists():
            log_content = log_file.read_text()

            # Add to summary table
            table_row = f"| {session_num} | {today} | {summary[:50]}{'...' if len(summary) > 50 else ''} | {new_streak} | {learning[:30]}{'...' if len(learning) > 30 else ''} |"

            # Find the table and add row
            if '|---|' in log_content:
                parts = log_content.split('|---|')
                if len(parts) >= 2:
                    table_end = parts[1].find('\n\n')
                    if table_end == -1:
                        table_end = len(parts[1])

                    new_log = parts[0] + '|---|' + parts[1][:table_end] + '\n' + table_row + parts[1][table_end:]
                    log_file.write_text(new_log)

        # Git sync
        git_sync(push=True, message=f"Streak: {challenge['name']} session {session_num} via Telegram")

        return True
    except Exception as e:
        logger.error(f"Failed to save check-in: {e}")
        return False


def create_challenge(name: str, challenge_type: str, goal: str, cadence: str) -> bool:
    """Create a new challenge."""
    try:
        # Create challenge ID from name
        challenge_id = re.sub(r'[^a-z0-9]+', '-', name.lower()).strip('-')
        challenge_dir = STREAK_PATH / 'challenges' / challenge_id
        challenge_dir.mkdir(parents=True, exist_ok=True)

        today = datetime.now().strftime('%Y-%m-%d')

        # Create challenge-config.md
        config_content = f"""# Challenge Config

Metadata for this challenge.

---

## Challenge Info

**Name:** {name}
**Type:** {challenge_type}
**Goal:** {goal}
**Cadence:** {cadence}
**Started:** {today}
**Priority:** 0

---

## Progress

**Check-ins:** 0
**Current Streak:** 0 days
**Longest Streak:** 0 days
**Status:** active

---

## Achievements

<!-- Earned achievements listed here -->
"""
        (challenge_dir / 'challenge-config.md').write_text(config_content)

        # Create challenge-log.md
        log_content = f"""# {name} Progress Log

**Goal:** {goal}
**Started:** {today}
**Cadence:** {cadence}

---

## Summary

| # | Date | Summary | Streak | Key Learning |
|---|------|---------|--------|--------------|

---

## Detailed Log

<!-- Detailed entries added below -->
"""
        (challenge_dir / 'challenge-log.md').write_text(log_content)

        # Create sessions folder
        (challenge_dir / 'sessions').mkdir(exist_ok=True)

        # Create other template files
        (challenge_dir / 'backlog.md').write_text(f"""# Backlog

Ideas and things to try for {name}.

---

## High Priority
- [ ]

## Medium Priority
- [ ]

## Someday/Maybe
- [ ]

---

## Completed
""")

        git_sync(push=True, message=f"Streak: Created new challenge '{name}' via Telegram")

        return True
    except Exception as e:
        logger.error(f"Failed to create challenge: {e}")
        return False


def check_user_allowed(user_id: int) -> bool:
    """Check if user is allowed to use the bot."""
    if not ALLOWED_USERS or ALLOWED_USERS == ['']:
        return True
    return str(user_id) in ALLOWED_USERS


# =============================================================================
# Command Handlers
# =============================================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send welcome message with main menu."""
    if not check_user_allowed(update.effective_user.id):
        await update.message.reply_text("Sorry, you're not authorized to use this bot.")
        return

    keyboard = [
        [
            InlineKeyboardButton("✓ Check In", callback_data='checkin'),
            InlineKeyboardButton("📋 List", callback_data='list'),
        ],
        [
            InlineKeyboardButton("📊 Stats", callback_data='stats'),
            InlineKeyboardButton("💡 Insights", callback_data='insights'),
        ],
        [
            InlineKeyboardButton("➕ New Challenge", callback_data='new'),
            InlineKeyboardButton("🔄 Switch", callback_data='switch'),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    challenge = get_active_challenge()

    if challenge:
        status_emoji = '🔥' if challenge['check_status'] == 'ok' else '⚠️' if challenge['check_status'] == 'due' else '❗'
        message = f"""*Streak Bot* 🎯

Active: *{challenge['name']}*
{status_emoji} Streak: {challenge['streak']} | Sessions: {challenge['check_ins']}

What would you like to do?"""
    else:
        message = """*Streak Bot* 🎯

No active challenge found.

Create one or switch to an existing challenge."""

    await update.message.reply_text(
        message,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def list_challenges(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List all challenges."""
    query = update.callback_query
    if query:
        await query.answer()

    challenges = get_all_challenges()

    if not challenges:
        message = "No challenges found.\n\nUse /new to create one!"
        if query:
            await query.edit_message_text(message)
        else:
            await update.message.reply_text(message)
        return

    # Group by status
    active = [c for c in challenges if c['status'] == 'active']
    paused = [c for c in challenges if c['status'] == 'paused']
    archived = [c for c in challenges if c['status'] == 'archived']

    lines = ["*Your Challenges*\n"]

    if active:
        lines.append("*Active:*")
        for c in active:
            emoji = '🔥' if c['check_status'] == 'ok' else '⚠️' if c['check_status'] == 'due' else '❗'
            lines.append(f"  {emoji} {c['name']} - {c['streak']} streak, {c['check_ins']} sessions")
        lines.append("")

    if paused:
        lines.append("*Paused:*")
        for c in paused:
            lines.append(f"  ⏸ {c['name']} - {c['check_ins']} sessions")
        lines.append("")

    if archived:
        lines.append(f"_{len(archived)} archived challenges_")

    keyboard = [[InlineKeyboardButton("« Back", callback_data='menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message = '\n'.join(lines)

    if query:
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')


async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show statistics for active challenge."""
    query = update.callback_query
    if query:
        await query.answer()

    challenge = get_active_challenge()

    if not challenge:
        message = "No active challenge.\n\nSwitch to a challenge first."
        keyboard = [[InlineKeyboardButton("« Back", callback_data='menu')]]
        if query:
            await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
        return

    # Calculate stats
    started = parse_date(challenge['started']) if challenge['started'] else None
    days_active = (datetime.now() - started).days if started else 0

    message = f"""*{challenge['name']} Statistics* 📊

*Progress*
• Sessions: {challenge['check_ins']}
• Days active: {days_active}
• Goal: {challenge['goal'] or 'Not set'}

*Streaks*
• Current: {challenge['streak']}
• Longest: {challenge['longest_streak']}
• Days since check-in: {challenge['days_since']}

*Info*
• Type: {challenge['type'] or 'Custom'}
• Cadence: {challenge['cadence'] or 'Daily'}
• Started: {challenge['started'] or 'Unknown'}"""

    keyboard = [
        [InlineKeyboardButton("✓ Check In", callback_data='checkin')],
        [InlineKeyboardButton("« Back", callback_data='menu')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if query:
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')


async def show_insights(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Show cross-challenge insights."""
    query = update.callback_query
    if query:
        await query.answer()

    challenges = get_all_challenges()
    active_challenges = [c for c in challenges if c['status'] == 'active']

    if len(active_challenges) < 2:
        message = "*Cross-Challenge Insights* 💡\n\nNeed 2+ active challenges to detect patterns.\n\nCreate another challenge to unlock insights!"
    else:
        # Basic insight generation
        total_sessions = sum(c['check_ins'] for c in active_challenges)
        types = set(c['type'] for c in active_challenges if c['type'])

        message = f"""*Cross-Challenge Insights* 💡

*Overview*
• {len(active_challenges)} active challenges
• {total_sessions} total sessions
• Types: {', '.join(types) if types else 'Mixed'}

*Patterns*
"""
        # Find best performing challenge
        best = max(active_challenges, key=lambda x: int(x['streak'].split()[0]))
        message += f"• Strongest streak: {best['name']} ({best['streak']})\n"

        # Find challenges needing attention
        overdue = [c for c in active_challenges if c['check_status'] == 'overdue']
        if overdue:
            message += f"• Needs attention: {', '.join(c['name'] for c in overdue)}\n"

    keyboard = [[InlineKeyboardButton("« Back", callback_data='menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if query:
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')


async def menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle main menu button."""
    query = update.callback_query
    await query.answer()

    keyboard = [
        [
            InlineKeyboardButton("✓ Check In", callback_data='checkin'),
            InlineKeyboardButton("📋 List", callback_data='list'),
        ],
        [
            InlineKeyboardButton("📊 Stats", callback_data='stats'),
            InlineKeyboardButton("💡 Insights", callback_data='insights'),
        ],
        [
            InlineKeyboardButton("➕ New Challenge", callback_data='new'),
            InlineKeyboardButton("🔄 Switch", callback_data='switch'),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    challenge = get_active_challenge()

    if challenge:
        status_emoji = '🔥' if challenge['check_status'] == 'ok' else '⚠️' if challenge['check_status'] == 'due' else '❗'
        message = f"""*Streak Bot* 🎯

Active: *{challenge['name']}*
{status_emoji} Streak: {challenge['streak']} | Sessions: {challenge['check_ins']}

What would you like to do?"""
    else:
        message = """*Streak Bot* 🎯

No active challenge found."""

    await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')


# =============================================================================
# Check-in Conversation
# =============================================================================

async def checkin_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start check-in conversation."""
    query = update.callback_query
    if query:
        await query.answer()

    challenge = get_active_challenge()

    if not challenge:
        message = "No active challenge. Create or switch to one first."
        keyboard = [[InlineKeyboardButton("« Back", callback_data='menu')]]
        if query:
            await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
        return ConversationHandler.END

    context.user_data['challenge'] = challenge

    status_text = ""
    if challenge['check_status'] == 'overdue':
        status_text = f"⚠️ {challenge['days_since']} days since last check-in"
    elif challenge['check_status'] == 'due':
        status_text = "📅 Check-in due today!"
    else:
        status_text = f"🔥 On track! ({challenge['days_since']} days since last)"

    message = f"""*Check In: {challenge['name']}*

{status_text}
Current streak: {challenge['streak']}

Ready to log your progress?"""

    keyboard = [
        [
            InlineKeyboardButton("✓ Yes, check in", callback_data='checkin_yes'),
            InlineKeyboardButton("✗ Not now", callback_data='checkin_no'),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if query:
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')

    return CHECKIN_CONFIRM


async def checkin_confirm(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle check-in confirmation."""
    query = update.callback_query
    await query.answer()

    if query.data == 'checkin_no':
        await query.edit_message_text("No problem! Come back when you're ready. 👋")
        return ConversationHandler.END

    await query.edit_message_text(
        "*What did you work on?*\n\nType a brief summary of your session:",
        parse_mode='Markdown'
    )

    return CHECKIN_SUMMARY


async def checkin_summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive summary."""
    context.user_data['summary'] = update.message.text

    keyboard = [
        [
            InlineKeyboardButton("🎉 Great", callback_data='feeling_great'),
            InlineKeyboardButton("👍 Good", callback_data='feeling_good'),
        ],
        [
            InlineKeyboardButton("😐 Okay", callback_data='feeling_okay'),
            InlineKeyboardButton("😓 Struggled", callback_data='feeling_struggled'),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "*How did it go?*",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

    return CHECKIN_FEELING


async def checkin_feeling(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive feeling."""
    query = update.callback_query
    await query.answer()

    feelings = {
        'feeling_great': 'Great! 🎉',
        'feeling_good': 'Good 👍',
        'feeling_okay': 'Okay 😐',
        'feeling_struggled': 'Struggled 😓',
    }
    context.user_data['feeling'] = feelings.get(query.data, 'Good')

    await query.edit_message_text(
        "*Any key learning?*\n\nMain takeaway from this session (or type /skip):",
        parse_mode='Markdown'
    )

    return CHECKIN_LEARNING


async def checkin_learning(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive learning."""
    text = update.message.text
    context.user_data['learning'] = '' if text == '/skip' else text

    await update.message.reply_text(
        "*What's next?*\n\nPlans for next session (or type /skip):",
        parse_mode='Markdown'
    )

    return CHECKIN_NEXT


async def checkin_next(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive next steps and save check-in."""
    text = update.message.text
    context.user_data['next'] = '' if text == '/skip' else text

    challenge = context.user_data['challenge']

    success = save_checkin(
        challenge,
        context.user_data['summary'],
        context.user_data['feeling'],
        context.user_data['learning'],
        context.user_data['next']
    )

    if success:
        new_sessions = challenge['check_ins'] + 1

        # Calculate new streak
        if challenge['days_since'] <= challenge['cadence_days']:
            new_streak = int(challenge['streak'].split()[0]) + 1
        else:
            new_streak = 1

        message = f"""✅ *Session {new_sessions} logged!*

Challenge: {challenge['name']}
Streak: {new_streak} days 🔥
Total sessions: {new_sessions}

Great work! See you next time. 💪"""

        keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data='menu')]]
        await update.message.reply_text(
            message,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "❌ Failed to save check-in. Please try again.",
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main Menu", callback_data='menu')]])
        )

    return ConversationHandler.END


async def checkin_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel check-in."""
    await update.message.reply_text(
        "Check-in cancelled.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main Menu", callback_data='menu')]])
    )
    return ConversationHandler.END


# =============================================================================
# New Challenge Conversation
# =============================================================================

async def new_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start new challenge conversation."""
    query = update.callback_query
    if query:
        await query.answer()

    keyboard = [
        [
            InlineKeyboardButton("📚 Learning", callback_data='type_learning'),
            InlineKeyboardButton("🔨 Building", callback_data='type_building'),
        ],
        [
            InlineKeyboardButton("💪 Fitness", callback_data='type_fitness'),
            InlineKeyboardButton("🎨 Creative", callback_data='type_creative'),
        ],
        [
            InlineKeyboardButton("✅ Habit", callback_data='type_habit'),
            InlineKeyboardButton("⚙️ Custom", callback_data='type_custom'),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    message = "*Create New Challenge* ➕\n\nWhat type of challenge?"

    if query:
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode='Markdown')

    return NEW_TYPE


async def new_type(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive challenge type."""
    query = update.callback_query
    await query.answer()

    types = {
        'type_learning': 'learning',
        'type_building': 'building',
        'type_fitness': 'fitness',
        'type_creative': 'creative',
        'type_habit': 'habit',
        'type_custom': 'custom',
    }
    context.user_data['new_type'] = types.get(query.data, 'custom')

    await query.edit_message_text(
        "*Challenge name?*\n\nShort name for your challenge (e.g., 'learn-rust', 'morning-workout'):",
        parse_mode='Markdown'
    )

    return NEW_NAME


async def new_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive challenge name."""
    context.user_data['new_name'] = update.message.text

    await update.message.reply_text(
        "*What's your goal?*\n\nOne sentence describing success:",
        parse_mode='Markdown'
    )

    return NEW_GOAL


async def new_goal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive challenge goal."""
    context.user_data['new_goal'] = update.message.text

    keyboard = [
        [
            InlineKeyboardButton("Daily", callback_data='cadence_daily'),
            InlineKeyboardButton("Every 2 days", callback_data='cadence_2'),
        ],
        [
            InlineKeyboardButton("Every 3 days", callback_data='cadence_3'),
            InlineKeyboardButton("Weekly", callback_data='cadence_weekly'),
        ],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "*How often will you check in?*",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

    return NEW_CADENCE


async def new_cadence(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Receive cadence and create challenge."""
    query = update.callback_query
    await query.answer()

    cadences = {
        'cadence_daily': 'Daily',
        'cadence_2': 'Every 2 days',
        'cadence_3': 'Every 3 days',
        'cadence_weekly': 'Weekly',
    }
    cadence = cadences.get(query.data, 'Daily')

    success = create_challenge(
        context.user_data['new_name'],
        context.user_data['new_type'],
        context.user_data['new_goal'],
        cadence
    )

    if success:
        message = f"""✅ *Challenge created!*

Name: {context.user_data['new_name']}
Type: {context.user_data['new_type']}
Goal: {context.user_data['new_goal']}
Cadence: {cadence}

Ready for your first check-in!"""

        keyboard = [
            [InlineKeyboardButton("✓ Check In Now", callback_data='checkin')],
            [InlineKeyboardButton("🏠 Main Menu", callback_data='menu')],
        ]
    else:
        message = "❌ Failed to create challenge. Please try again."
        keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data='menu')]]

    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

    return ConversationHandler.END


async def new_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel new challenge."""
    await update.message.reply_text(
        "Challenge creation cancelled.",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🏠 Main Menu", callback_data='menu')]])
    )
    return ConversationHandler.END


# =============================================================================
# Switch Challenge
# =============================================================================

async def switch_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start switch conversation."""
    query = update.callback_query
    if query:
        await query.answer()

    challenges = get_all_challenges()
    active = [c for c in challenges if c['status'] == 'active']

    if not active:
        message = "No challenges to switch to.\n\nCreate one first!"
        keyboard = [[InlineKeyboardButton("« Back", callback_data='menu')]]
        if query:
            await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(keyboard))
        return ConversationHandler.END

    keyboard = []
    for c in active:
        keyboard.append([InlineKeyboardButton(
            f"{c['name']} ({c['streak']})",
            callback_data=f"switch_{c['id']}"
        )])
    keyboard.append([InlineKeyboardButton("« Cancel", callback_data='menu')])

    message = "*Switch Challenge* 🔄\n\nSelect a challenge:"

    if query:
        await query.edit_message_text(message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')
    else:
        await update.message.reply_text(message, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    return SWITCH_SELECT


async def switch_select(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle switch selection."""
    query = update.callback_query
    await query.answer()

    if query.data == 'menu':
        return ConversationHandler.END

    challenge_id = query.data.replace('switch_', '')

    # For now, we don't have a separate active.md - the "active" challenge
    # is just the one with status=active. In a multi-challenge scenario,
    # you'd update an active.md file here.

    challenges = get_all_challenges()
    selected = next((c for c in challenges if c['id'] == challenge_id), None)

    if selected:
        message = f"""✅ *Switched to: {selected['name']}*

Streak: {selected['streak']}
Sessions: {selected['check_ins']}

Ready to check in?"""

        keyboard = [
            [InlineKeyboardButton("✓ Check In", callback_data='checkin')],
            [InlineKeyboardButton("🏠 Main Menu", callback_data='menu')],
        ]
    else:
        message = "❌ Challenge not found."
        keyboard = [[InlineKeyboardButton("🏠 Main Menu", callback_data='menu')]]

    await query.edit_message_text(
        message,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

    return ConversationHandler.END


# =============================================================================
# Scheduled Notifications
# =============================================================================

async def send_scheduled_notification(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send daily notification for due/overdue challenges."""
    logger.info("Running scheduled notification check...")

    # Sync with git first
    git_sync(pull=True)

    # Get all challenges and filter for due/overdue
    challenges = get_all_challenges()
    due = [c for c in challenges if c['check_status'] == 'due']
    overdue = [c for c in challenges if c['check_status'] == 'overdue']

    if not due and not overdue:
        logger.info("No due/overdue challenges - skipping notification")
        return

    # Build notification message
    lines = ["🔔 *Streak Check-in Reminder*\n"]

    if overdue:
        lines.append("*❗ Overdue:*")
        for c in overdue:
            days_over = c['days_since'] - c['cadence_days']
            lines.append(f"• {c['name']} ({days_over}d overdue)")
        lines.append("")

    if due:
        lines.append("*📅 Due Today:*")
        for c in due:
            lines.append(f"• {c['name']} (streak: {c['streak']})")
        lines.append("")

    lines.append("_Tap /streak to check in_")

    message = '\n'.join(lines)

    # Send to all allowed users
    if ALLOWED_USERS:
        for chat_id in ALLOWED_USERS:
            chat_id = chat_id.strip()
            if chat_id:
                try:
                    keyboard = [
                        [InlineKeyboardButton("✓ Check In Now", callback_data='checkin')],
                        [InlineKeyboardButton("📋 List All", callback_data='list')],
                    ]
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        parse_mode='Markdown',
                        reply_markup=InlineKeyboardMarkup(keyboard)
                    )
                    logger.info(f"Notification sent to {chat_id}")
                except Exception as e:
                    logger.error(f"Failed to send notification to {chat_id}: {e}")
    else:
        logger.warning("ALLOWED_USERS not set - cannot send scheduled notifications")
        logger.warning("Set ALLOWED_USERS environment variable with your chat ID")


def setup_scheduled_notifications(application: Application) -> None:
    """Set up the daily notification job."""
    if not NOTIFICATION_ENABLED:
        logger.info("Scheduled notifications disabled")
        return

    if not ALLOWED_USERS:
        logger.warning("ALLOWED_USERS not set - scheduled notifications won't be sent")
        logger.warning("Set ALLOWED_USERS=your_chat_id to receive daily reminders")
        return

    job_queue = application.job_queue

    # Schedule daily notification
    from datetime import time as dt_time
    try:
        import pytz
        tz = pytz.timezone(TIMEZONE)
    except:
        # Fallback if pytz not available
        tz = None
        logger.warning(f"pytz not available, using UTC for notifications")

    notification_time = dt_time(hour=NOTIFICATION_HOUR, minute=NOTIFICATION_MINUTE, tzinfo=tz)

    job_queue.run_daily(
        send_scheduled_notification,
        time=notification_time,
        name='daily_notification'
    )

    logger.info(f"Scheduled notifications enabled at {NOTIFICATION_HOUR:02d}:{NOTIFICATION_MINUTE:02d} {TIMEZONE}")


# =============================================================================
# Main
# =============================================================================

def main() -> None:
    """Start the bot."""
    if not TELEGRAM_BOT_TOKEN:
        print("Error: TELEGRAM_BOT_TOKEN environment variable not set")
        print("Export it or add to .env file")
        return

    if not STREAK_PATH.exists():
        print(f"Warning: Streak path {STREAK_PATH} does not exist")
        print("Creating directory...")
        STREAK_PATH.mkdir(parents=True, exist_ok=True)
        (STREAK_PATH / 'challenges').mkdir(exist_ok=True)

    # Create application
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    # Check-in conversation handler
    checkin_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(checkin_start, pattern='^checkin$'),
            CommandHandler('streak', checkin_start),
            CommandHandler('checkin', checkin_start),
        ],
        states={
            CHECKIN_CONFIRM: [CallbackQueryHandler(checkin_confirm, pattern='^checkin_')],
            CHECKIN_SUMMARY: [MessageHandler(filters.TEXT & ~filters.COMMAND, checkin_summary)],
            CHECKIN_FEELING: [CallbackQueryHandler(checkin_feeling, pattern='^feeling_')],
            CHECKIN_LEARNING: [MessageHandler(filters.TEXT, checkin_learning)],
            CHECKIN_NEXT: [MessageHandler(filters.TEXT, checkin_next)],
        },
        fallbacks=[CommandHandler('cancel', checkin_cancel)],
    )

    # New challenge conversation handler
    new_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(new_start, pattern='^new$'),
            CommandHandler('new', new_start),
        ],
        states={
            NEW_TYPE: [CallbackQueryHandler(new_type, pattern='^type_')],
            NEW_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, new_name)],
            NEW_GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, new_goal)],
            NEW_CADENCE: [CallbackQueryHandler(new_cadence, pattern='^cadence_')],
        },
        fallbacks=[CommandHandler('cancel', new_cancel)],
    )

    # Switch conversation handler
    switch_handler = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(switch_start, pattern='^switch$'),
            CommandHandler('switch', switch_start),
        ],
        states={
            SWITCH_SELECT: [CallbackQueryHandler(switch_select, pattern='^switch_|^menu$')],
        },
        fallbacks=[CommandHandler('cancel', checkin_cancel)],
    )

    # Add handlers
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('list', list_challenges))
    application.add_handler(CommandHandler('stats', show_stats))
    application.add_handler(CommandHandler('insights', show_insights))

    application.add_handler(checkin_handler)
    application.add_handler(new_handler)
    application.add_handler(switch_handler)

    # Callback handlers for menu buttons
    application.add_handler(CallbackQueryHandler(menu_callback, pattern='^menu$'))
    application.add_handler(CallbackQueryHandler(list_challenges, pattern='^list$'))
    application.add_handler(CallbackQueryHandler(show_stats, pattern='^stats$'))
    application.add_handler(CallbackQueryHandler(show_insights, pattern='^insights$'))

    # Set up scheduled notifications
    setup_scheduled_notifications(application)

    # Start polling
    print(f"Starting Streak Bot...")
    print(f"Streak path: {STREAK_PATH}")
    print(f"Git auto-sync: {GIT_AUTO_SYNC}")
    print(f"Allowed users: {ALLOWED_USERS if ALLOWED_USERS else 'All'}")
    print(f"Notifications: {'Enabled at ' + str(NOTIFICATION_HOUR).zfill(2) + ':' + str(NOTIFICATION_MINUTE).zfill(2) + ' ' + TIMEZONE if NOTIFICATION_ENABLED else 'Disabled'}")

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
