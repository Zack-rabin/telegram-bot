#!/usr/bin/env python3
"""
Telegram Bot with Daily and Weekly Motivational Messages
Features: Subscriptions, Scheduling, Error Handling
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from telegram.error import TelegramError, NetworkError
import random
from datetime import datetime, time, timedelta
import pytz
import json
from pathlib import Path

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token - REPLACE WITH YOUR ACTUAL TOKEN
BOT_TOKEN = "7860194776:AAG_C99R75Z9bZjoGnQxsM0Fp7CW6BUFj_o"

# Store subscribed members and their preferences
subscribed_members = set()
subscription_preferences = {}  # chat_id -> "daily", "weekly", or "both"

# Group management
motivation_group_id = None  # group chat id where quotes will be posted
motivation_group_invite = None  # stored invite link (str)
motivation_group_members = set()  # user ids who accepted to join the group
STATE_FILE = Path(__file__).parent / "state.json"


def save_state():
    """Persist group state to disk"""
    try:
        data = {
            "motivation_group_id": motivation_group_id,
            "motivation_group_invite": motivation_group_invite,
            "motivation_group_members": list(motivation_group_members),
        }
        STATE_FILE.write_text(json.dumps(data))
        logger.info("State saved to %s", STATE_FILE)
    except Exception as e:
        logger.error(f"Failed to save state: {e}")


def load_state():
    """Load persisted state from disk if present"""
    global motivation_group_id, motivation_group_invite, motivation_group_members
    try:
        if not STATE_FILE.exists():
            return
        data = json.loads(STATE_FILE.read_text())
        motivation_group_id = data.get("motivation_group_id")
        motivation_group_invite = data.get("motivation_group_invite")
        members = data.get("motivation_group_members") or []
        motivation_group_members = set(members)
        logger.info("Loaded state from %s", STATE_FILE)
    except Exception as e:
        logger.error(f"Failed to load state: {e}")

# Motivational quotes
DAILY_QUOTES = [
    "🌟 You are capable of amazing things! Keep pushing forward!",
    "💪 Every day is a new opportunity to become a better version of yourself!",
    "🚀 Don't watch the clock; do what it does. Keep going!",
    "✨ Your potential is limitless. Believe in yourself!",
    "🎯 Success is the sum of small efforts repeated day in and day out!",
    "🌈 The only way to do great work is to love what you do!",
    "💫 You've got this! Keep moving forward with confidence!",
    "🏆 Champions aren't made in the gyms. They are made from something they have deep inside them - a desire!",
    "🔥 Don't let yesterday take up too much of today. Focus on the present!",
    "⭐ You are destined for greatness. Start believing it today!",
    "🌻 Every challenge is an opportunity to grow stronger!",
    "💎 Your determination will define your destiny!",
    "🎪 Life is 10% what happens to you and 90% how you react to it!",
    "🌙 The future belongs to those who believe in the beauty of their dreams!",
    "🎨 You are a work of art in progress. Keep creating!"
]

# Weekly insights
WEEKLY_INSIGHTS = [
    "📚 <b>Weekly Wisdom:</b>\n\nReflect on your progress this week. Every step forward, no matter how small, is a victory worth celebrating! 🎉",
    "🔮 <b>Weekly Insight:</b>\n\nSuccess is not a destination, it's a journey. Enjoy the process, learn from setbacks, and keep growing! 🌱",
    "💡 <b>Weekly Thought:</b>\n\nThis week, focus on progress over perfection. Consistency beats intensity every single time! 💯",
    "🎯 <b>Weekly Challenge:</b>\n\nTake on one challenge this week that scares you a little. Growth happens outside comfort zones! 🚀",
    "🌟 <b>Weekly Reminder:</b>\n\nYou are stronger than you think. You have overcome 100% of your bad days so far! 💪",
    "✨ <b>Weekly Message:</b>\n\nBe kind to yourself this week. You're doing better than you think, and your efforts matter! 💝",
    "🏅 <b>Weekly Boost:</b>\n\nCelebrate your wins this week, big or small. You've earned it! Take time to appreciate your progress! 🎊"
]

def get_random_quote():
    """Get a random motivational quote"""
    return random.choice(DAILY_QUOTES)

def get_random_insight():
    """Get a random weekly insight"""
    return random.choice(WEEKLY_INSIGHTS)

# ==================== COMMAND HANDLERS ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    try:
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        # Check if new subscriber
        is_new = user_id not in subscribed_members
        subscribed_members.add(user_id)
        
        message = "Hello! Welcome to the Telegram bot.\nUse /help for available commands."
        
        if is_new:
            message += "\n\n🎉 You're now added to our community! Use /subscribe to enable motivational messages!"
            logger.info(f"New user started bot: {user_id}")
        else:
            message += "\n\n✅ Welcome back!"
            logger.info(f"Returning user: {user_id}")
        
        await context.bot.send_message(chat_id=chat_id, text=message)
    except TelegramError as e:
        logger.error(f"Telegram error in /start: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in /start: {e}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    try:
        chat_id = update.effective_chat.id
        
        help_text = """Available commands:
/start - Start the bot
/help - Show this help message
/info - Get bot information
/share - Share bot with contacts and groups
/motivate - Get a motivational message
/subscribe - Choose subscription type
/unsubscribe - Stop receiving messages
/subscribers - Show subscriber count"""
        
        await context.bot.send_message(chat_id=chat_id, text=help_text)
        logger.info(f"Help command used by chat: {chat_id}")
    except TelegramError as e:
        logger.error(f"Telegram error in /help: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in /help: {e}")

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /info command"""
    try:
        chat_id = update.effective_chat.id
        
        info_text = """<b>🤖 Telegram Bot Information</b>

<b>Features:</b>
✅ Daily Motivational Messages
✅ Weekly Deep Insights
✅ Flexible Subscriptions
✅ Community Sharing
✅ Subscriber Statistics

<b>How It Works:</b>
1. Use /subscribe to choose your preference
2. Receive daily messages at 9 AM
3. Get weekly insights on Mondays
4. Share with friends and groups

<b>Support:</b>
Use /help for all available commands"""
        
        await context.bot.send_message(chat_id=chat_id, text=info_text, parse_mode='HTML')
        logger.info(f"Info command used by chat: {chat_id}")
    except TelegramError as e:
        logger.error(f"Telegram error in /info: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in /info: {e}")

async def motivate_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /motivate command"""
    try:
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        is_new = user_id not in subscribed_members
        subscribed_members.add(user_id)
        
        quote = get_random_quote()
        message = quote
        
        if is_new:
            message += "\n\n✨ You've been added to our subscriber list! Use /subscribe to choose your preference!"
            logger.info(f"New subscriber from /motivate: {user_id}")
        
        await context.bot.send_message(chat_id=chat_id, text=message)
        logger.info(f"Motivational message sent to chat: {chat_id}")
    except TelegramError as e:
        logger.error(f"Telegram error in /motivate: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in /motivate: {e}")

async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /subscribe command with subscription options"""
    try:
        chat_id = update.effective_chat.id
        
        # Create inline keyboard
        keyboard = [
            [InlineKeyboardButton("📅 Daily Motivation (9 AM)", callback_data="sub_daily")],
            [InlineKeyboardButton("📆 Weekly Insights (Monday 9 AM)", callback_data="sub_weekly")],
            [InlineKeyboardButton("🎯 Both (Daily + Weekly)", callback_data="sub_both")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = """<b>🎁 Choose Your Subscription</b>

<b>📅 Daily:</b> Get motivated every day at midnight

<b>📆 Weekly:</b> Deep insights every Monday at midnight

<b>🎯 Both:</b> Daily motivation + Weekly insights

Select an option below:"""
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
        logger.info(f"Subscription menu shown to chat: {chat_id}")
    except TelegramError as e:
        logger.error(f"Telegram error in /subscribe: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in /subscribe: {e}")

async def unsubscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /unsubscribe command"""
    try:
        user_id = update.effective_user.id
        chat_id = update.effective_chat.id
        
        subscribed_members.discard(user_id)
        subscription_preferences.pop(chat_id, None)
        
        message = "❌ You've been unsubscribed from all messages.\n\nUse /subscribe anytime to re-subscribe! 📨"
        
        await context.bot.send_message(chat_id=chat_id, text=message)
        logger.info(f"User unsubscribed: {user_id}")
    except TelegramError as e:
        logger.error(f"Telegram error in /unsubscribe: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in /unsubscribe: {e}")

async def share_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /share command for affiliation"""
    try:
        chat_id = update.effective_chat.id
        
        keyboard = [
            [InlineKeyboardButton("📱 Share to Contacts", url="https://t.me/share/url?url=https://t.me/YOUR_BOT_USERNAME_HERE&text=Check%20out%20this%20amazing%20Telegram%20bot!")],
            [InlineKeyboardButton("👥 Share to Groups", url="https://t.me/share/url?url=https://t.me/YOUR_BOT_USERNAME_HERE&text=Check%20out%20this%20bot!")],
            [InlineKeyboardButton("🔗 Get Bot Link", url="https://t.me/YOUR_BOT_USERNAME_HERE")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = """🌟 <b>Help us grow!</b>

Share this bot with your contacts and groups:

📱 <b>Share to Contacts:</b> Send the bot link to your saved contacts
👥 <b>Share to Groups:</b> Invite the bot to your favorite groups
🔗 <b>Get Bot Link:</b> Get the direct link to add this bot

Thank you for helping us grow! 🚀"""
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode='HTML',
            reply_markup=reply_markup
        )
        logger.info(f"Share command used by chat: {chat_id}")
    except TelegramError as e:
        logger.error(f"Telegram error in /share: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in /share: {e}")

async def subscribers_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /subscribers command"""
    try:
        chat_id = update.effective_chat.id
        
        message = f"""📊 <b>Subscriber Statistics</b>

Total Subscribers: <b>{len(subscribed_members)}</b>

Thank you for being part of our community! 🙏"""
        
        await context.bot.send_message(
            chat_id=chat_id,
            text=message,
            parse_mode='HTML'
        )
        logger.info(f"Subscriber count sent to chat: {chat_id}")
    except TelegramError as e:
        logger.error(f"Telegram error in /subscribers: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in /subscribers: {e}")

# ==================== CALLBACK HANDLERS ====================

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button clicks for subscriptions"""
    try:
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        chat_id = query.message.chat.id
        callback_data = query.data
        
        if callback_data == "sub_daily":
            sub_type = "daily"
            confirm = "✅ You've subscribed to <b>Daily Motivation</b>!\n\nYou'll receive motivational messages every day at midnight. 📅"
        elif callback_data == "sub_weekly":
            sub_type = "weekly"
            confirm = "✅ You've subscribed to <b>Weekly Insights</b>!\n\nYou'll receive deep insights every Monday at midnight. 📆"
        elif callback_data == "sub_both":
            sub_type = "both"
            confirm = "✅ You've subscribed to <b>Both Daily & Weekly</b>!\n\nDaily motivation at midnight + Weekly insights on Mondays! 🎯"
        else:
            logger.warning(f"Unknown callback data: {callback_data}")
            return
        
        subscription_preferences[chat_id] = sub_type
        subscribed_members.add(user_id)
        
        await query.edit_message_text(
            text=confirm,
            parse_mode='HTML'
        )
        
        # Send immediate motivational message upon subscription
        try:
            quote = get_random_quote()
            await context.bot.send_message(
                chat_id=chat_id,
                text=f"Welcome! Here's your first motivation to get you started:\n\n{quote}",
                parse_mode='HTML'
            )
            logger.info(f"Sent welcome motivation to new subscriber {user_id}")
        except TelegramError as e:
            logger.warning(f"Failed to send welcome message: {e}")
        
        logger.info(f"Subscription updated for user {user_id}: {sub_type}")
    except TelegramError as e:
        logger.error(f"Telegram error in callback: {e}")
    except Exception as e:
        logger.error(f"Unexpected error in callback: {e}")


async def register_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Register the current group (bot must be admin) so the bot will post quotes there."""
    global motivation_group_id, motivation_group_invite
    try:
        chat = update.effective_chat
        chat_id = chat.id
        # Only allow group/supergroup registration
        if chat.type not in ("group", "supergroup"):
            await context.bot.send_message(chat_id=chat_id, text="Please run this command in the group chat you want to register.")
            return

        # Only allow group admins to register the group
        try:
            requester = update.effective_user
            member = await context.bot.get_chat_member(chat_id=chat_id, user_id=requester.id)
            if member.status not in ("administrator", "creator"):
                await context.bot.send_message(chat_id=chat_id, text="Only a group admin may register this group for motivational messages. Please ask an admin to run /register_group.")
                return
        except Exception:
            # If we cannot verify admin status, proceed but warn
            await context.bot.send_message(chat_id=chat_id, text="Warning: Unable to verify admin status. Ensure the bot is admin and has permissions to create invite links.")

        # Create a permanent invite link (bot must be admin with invite_link right)
        try:
            invite = await context.bot.create_chat_invite_link(chat_id=chat_id)
            motivation_group_invite = invite.invite_link
        except Exception:
            motivation_group_invite = None

        motivation_group_id = chat_id
        save_state()
        if motivation_group_invite:
            await context.bot.send_message(chat_id=chat_id, text=f"✅ This group is now registered for motivational quotes. Invite link created and saved.")
        else:
            await context.bot.send_message(chat_id=chat_id, text="✅ This group is now registered for motivational quotes. (Could not create invite link — please grant the bot invite permissions)")
        logger.info(f"Group registered for motivation: {chat_id}")
    except Exception as e:
        logger.error(f"Error in register_group: {e}")


async def join_group(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send the stored invite link to users who want to join the motivation group."""
    global motivation_group_id, motivation_group_invite
    try:
        user_chat = update.effective_chat.id
        if motivation_group_id is None:
            await context.bot.send_message(chat_id=user_chat, text="No motivation group is registered yet. Ask an admin to register the group in the group chat using /register_group.")
            return

        # Ensure we have an invite; try to create one if missing
        if not motivation_group_invite:
            try:
                invite = await context.bot.create_chat_invite_link(chat_id=motivation_group_id)
                motivation_group_invite = invite.invite_link
            except Exception:
                motivation_group_invite = None

        if motivation_group_invite:
            keyboard = [[InlineKeyboardButton("Accept Invite →", url=motivation_group_invite)]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(chat_id=user_chat, text="Click below to join the motivation group:", reply_markup=reply_markup)
            logger.info(f"Sent group invite to user chat: {user_chat}")
        else:
            await context.bot.send_message(chat_id=user_chat, text="Unable to generate an invite link. Make sure the bot is admin in the registered group and has permission to create invite links.")
    except Exception as e:
        logger.error(f"Error in join_group: {e}")



async def new_group_member_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle new_chat_members events to track who joined the registered group."""
    global motivation_group_id, motivation_group_members
    try:
        if update.message is None or update.message.new_chat_members is None:
            return
        chat_id = update.effective_chat.id
        if motivation_group_id is None or chat_id != motivation_group_id:
            return

        for user in update.message.new_chat_members:
            motivation_group_members.add(user.id)
            await context.bot.send_message(chat_id=chat_id, text=f"Welcome {user.full_name}! Thanks for joining the motivation group.")
            logger.info(f"User {user.id} joined motivation group {chat_id}")
            # Persist membership
            try:
                save_state()
            except Exception:
                pass
    except Exception as e:
        logger.error(f"Error in new_group_member_handler: {e}")


async def group_members_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """List known members who have joined via the bot."""
    global motivation_group_members, motivation_group_id
    try:
        chat_id = update.effective_chat.id
        if motivation_group_id is None:
            await context.bot.send_message(chat_id=chat_id, text="No motivation group is registered yet.")
            return

        members_list = "\n".join([str(uid) for uid in sorted(motivation_group_members)]) or "(no members tracked yet)"
        await context.bot.send_message(chat_id=chat_id, text=f"Tracked group members:\n{members_list}")
    except Exception as e:
        logger.error(f"Error in group_members_command: {e}")


async def send_group_motivation(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a random quote to the registered group every 5 minutes."""
    global motivation_group_id
    try:
        if motivation_group_id is None:
            return

        quote = get_random_quote()
        await context.bot.send_message(chat_id=motivation_group_id, text=f"🔥 <b>Motivation</b>\n\n{quote}", parse_mode='HTML')
        logger.info(f"Sent group motivation to {motivation_group_id}")
    except Exception as e:
        logger.error(f"Error in send_group_motivation: {e}")

# ==================== SCHEDULED TASKS ====================

async def send_daily_motivation(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send daily motivational messages at 9 AM"""
    try:
        logger.info("Sending daily motivational messages...")
        quote = get_random_quote()
        
        for chat_id in subscription_preferences.keys():
            sub_type = subscription_preferences[chat_id]
            if sub_type in ["daily", "both"]:
                try:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=f"🌅 <b>Good Morning!</b>\n\n{quote}",
                        parse_mode='HTML'
                    )
                    logger.info(f"Daily message sent to chat: {chat_id}")
                except TelegramError as e:
                    logger.warning(f"Failed to send daily message to {chat_id}: {e}")
    except Exception as e:
        logger.error(f"Error in send_daily_motivation: {e}")

async def send_weekly_motivation(context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send weekly motivational messages on Monday at 9 AM"""
    try:
        logger.info("Sending weekly insights...")
        insight = get_random_insight()
        
        for chat_id in subscription_preferences.keys():
            sub_type = subscription_preferences[chat_id]
            if sub_type in ["weekly", "both"]:
                try:
                    await context.bot.send_message(
                        chat_id=chat_id,
                        text=f"🌟 <b>Monday Motivation - Start Your Week Strong!</b>\n\n{insight}",
                        parse_mode='HTML'
                    )
                    logger.info(f"Weekly message sent to chat: {chat_id}")
                except TelegramError as e:
                    logger.warning(f"Failed to send weekly message to {chat_id}: {e}")
    except Exception as e:
        logger.error(f"Error in send_weekly_motivation: {e}")

# ==================== MAIN FUNCTION ====================

def main():
    """Start the bot"""
    # Load persisted state before starting
    load_state()
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("[ERROR] BOT_TOKEN not set!")
        print("Please replace 'YOUR_BOT_TOKEN_HERE' with your actual bot token from @BotFather")
        return
    
    reconnect_attempts = 0
    max_reconnect_attempts = 5
    
    while reconnect_attempts < max_reconnect_attempts:
        try:
            # Create application
            app = Application.builder().token(BOT_TOKEN).build()
            
            # Add command handlers
            app.add_handler(CommandHandler("start", start))
            app.add_handler(CommandHandler("help", help_command))
            app.add_handler(CommandHandler("info", info_command))
            app.add_handler(CommandHandler("motivate", motivate_command))
            app.add_handler(CommandHandler("subscribe", subscribe_command))
            app.add_handler(CommandHandler("unsubscribe", unsubscribe_command))
            app.add_handler(CommandHandler("share", share_command))
            app.add_handler(CommandHandler("subscribers", subscribers_command))
            
            # Add callback handler for buttons
            app.add_handler(CallbackQueryHandler(button_callback))

            # Group management handlers
            app.add_handler(CommandHandler("register_group", register_group))
            app.add_handler(CommandHandler("join_group", join_group))
            app.add_handler(CommandHandler("group_members", group_members_command))
            # Track new members joining the registered group
            app.add_handler(MessageHandler(filters.StatusUpdate.NEW_CHAT_MEMBERS, new_group_member_handler))
            
            # Add jobs for scheduled messages using job_queue
            job_queue = app.job_queue
            
            # Schedule daily messages at midnight (00:00)
            job_queue.run_daily(
                send_daily_motivation,
                time=time(hour=0, minute=0)
            )
            
            # Schedule weekly messages on Monday at midnight (00:00)
            job_queue.run_daily(
                send_weekly_motivation,
                time=time(hour=0, minute=0),
                days=(0,)
            )

            # Schedule group motivational quotes every 5 minutes
            job_queue.run_repeating(send_group_motivation, interval=300, first=10)
            
            logger.info("Bot started successfully!")
            print("[SUCCESS] Bot is running! Press Ctrl+C to stop.")
            reconnect_attempts = 0
            
            # Start the bot
            app.run_polling(allowed_updates=["message", "callback_query"])
            
        except NetworkError as e:
            reconnect_attempts += 1
            logger.error(f"Network error (attempt {reconnect_attempts}/{max_reconnect_attempts}): {e}")
            print(f"[NETWORK ERROR] Connection failed. Retrying in 10 seconds... ({reconnect_attempts}/{max_reconnect_attempts})")
            if reconnect_attempts < max_reconnect_attempts:
                import time as time_module
                time_module.sleep(10)
            else:
                print("[FATAL] Max reconnection attempts reached. Check your internet connection.")
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
            print("\n[INFO] Bot stopped by user")
            return
        except Exception as e:
            reconnect_attempts += 1
            logger.error(f"Error (attempt {reconnect_attempts}/{max_reconnect_attempts}): {e}")
            print(f"[ERROR] {e}")
            if reconnect_attempts < max_reconnect_attempts:
                import time as time_module
                time_module.sleep(10)
                print(f"[INFO] Retrying... ({reconnect_attempts}/{max_reconnect_attempts})")
            else:
                print("[FATAL] Max reconnection attempts reached.")

if __name__ == '__main__':
    main()
