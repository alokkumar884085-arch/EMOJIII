import logging
import random
import string
import time
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import asyncio
import re

# ============ CONFIGURATION ============
TOKEN = "8904097497:AAGazvlppLfBymhWP18Cjq7Hdi2XSc0DZvo"
OWNER_ID = 8785590284

# ============ TIERS WITH EMOJIS ============
TIERS = {
    "A": {
        "name": "✨ BASIC PREMIUM",
        "color": "🟢",
        "emoji_count": 70,
        "emojis": [
            "✨", "⭐", "🌟", "💫", "🌠", "☄️", "💥", "⚡", "🔥", "🌈",
            "🌸", "🌺", "🌹", "🌷", "🌻", "🌼", "💐", "🌿", "🌱", "🌳",
            "🌴", "🌵", "🌾", "🌽", "🍀", "☘️", "🍃", "🍂", "🍁", "🍄",
            "☀️", "🌤️", "⛅", "🌥️", "☁️", "🌦️", "🌧️", "⛈️", "🌨️", "❄️",
            "☃️", "⛄", "💨", "🌫️", "🌬️", "🪐", "🌍", "🌎", "🌏", "🌕",
            "🦋", "🐝", "🐞", "🦄", "🐉", "🦁", "🐯", "🐺", "🐻", "🐼",
            "🐨", "🦊", "🐰", "🐭", "🐹", "🐱", "🐶", "🦝", "🦡", "🦔",
            "🐠", "🐟", "🐬", "🐳", "🐋", "🦈", "🐙", "🦑", "🐚", "🌊",
            "🏝️", "🏖️", "⛵", "🚢", "⚓", "🛳️", "🚤", "🛥️", "🏄", "🏊"
        ],
        "access": [],
        "price": "FREE"
    },
    "B": {
        "name": "💎 SILVER PREMIUM",
        "color": "🔵",
        "emoji_count": 80,
        "emojis": [
            "💎", "👑", "🏆", "🥇", "🥈", "🥉", "🎖️", "💠", "🔮", "💜",
            "💙", "💚", "💛", "🧡", "❤️", "🖤", "🤍", "🤎", "💗", "💖",
            "💝", "💞", "💕", "❣️", "💋", "💘", "💟", "🩷", "🩵", "🩶",
            "💻", "🖥️", "⌨️", "🖱️", "🖨️", "📱", "📲", "☎️", "📞", "📟",
            "📠", "🔋", "🪫", "🔌", "💡", "🔦", "🕯️", "🧯", "🛢️", "💸",
            "💵", "💶", "💷", "💴", "💰", "🪙", "💳", "🧾", "📊", "📈",
            "🎵", "🎶", "🎼", "🎹", "🥁", "🎷", "🎺", "🎸", "🎻", "🎧",
            "🎤", "🎭", "🎪", "🎨", "🎬", "🎮", "🕹️", "🎲", "🎯", "🎱",
            "⚽", "🏀", "🏈", "⚾", "🎾", "🏐", "🏉", "🎱", "🎳", "🏏",
            "🏑", "🏒", "🥅", "⛳", "🏌️", "🏄", "🏊", "🤽", "🧗", "🚴"
        ],
        "access": ["A"],
        "price": "₹99/month"
    },
    "C": {
        "name": "🌟 GOLD PREMIUM",
        "color": "🟡",
        "emoji_count": 90,
        "emojis": [
            "🌟", "⭐", "🌠", "☀️", "🌈", "🎆", "🎇", "🌅", "🌄", "🎠",
            "🎢", "🎡", "🏰", "🗼", "🎑", "🌉", "🌌", "🌊", "🌋", "🗻",
            "🪐", "☄️", "💫", "⭐", "🌟", "✨", "⚡", "🔥", "💥", "🎯",
            "🚀", "🛸", "👽", "🤖", "👾", "🧠", "💡", "🔮", "🧬", "⚗️",
            "🏛️", "⛩️", "🕍", "⛪", "🕌", "🛕", "🕋", "🗽", "🗿", "🏗️",
            "🎊", "🎉", "🎈", "🎀", "🎁", "🎄", "🎃", "🎐", "🏮", "🧨",
            "✨", "🪅", "🎆", "🎇", "🪩", "🎭", "🎪", "🎨", "🎬", "🎤",
            "💎", "👑", "💰", "💳", "🪙", "💸", "💵", "💶", "💷", "💴",
            "📿", "🧿", "🔯", "🕎", "☯️", "☮️", "✝️", "☪️", "🕉️", "☸️"
        ],
        "access": ["A", "B"],
        "price": "₹199/month"
    },
    "D": {
        "name": "👑 PLATINUM PREMIUM",
        "color": "🟣",
        "emoji_count": 100,
        "emojis": [
            "👑", "💎", "⭐", "🌟", "✨", "🔥", "💫", "🌈", "🎆", "🎇",
            "🌠", "💠", "🔮", "💜", "💙", "💚", "💛", "🧡", "❤️", "🖤",
            "🤍", "💝", "💖", "💗", "💓", "💞", "💕", "❣️", "💋", "💘",
            "💟", "🩷", "🩵", "🩶", "🩹", "💉", "💊", "🩺", "📿", "🧿",
            "🖥️", "⌨️", "🖱️", "🖨️", "📱", "📲", "☎️", "📞", "📟", "📠",
            "🔋", "🪫", "🔌", "💡", "🔦", "🕯️", "🧯", "🛢️", "💸", "💵",
            "💶", "💷", "💴", "💰", "🪙", "💳", "🧾", "📊", "📈", "📉",
            "⚽", "🏀", "🏈", "⚾", "🎾", "🏐", "🏉", "🎱", "🎳", "🏏",
            "🏑", "🏒", "🥅", "⛳", "🏌️", "🏄", "🏊", "🤽", "🧗", "🚴",
            "🚵", "🏇", "⛸️", "🏂", "⛷️", "🎿", "🏋️", "🤼", "🤸", "🤾",
            "🪐", "☄️", "💫", "⭐", "🌟", "✨", "⚡", "🔥", "💥", "🎯",
            "🚀", "🛸", "👽", "🤖", "👾", "🧠", "💡", "🔮", "🧬", "⚗️",
            "🔭", "🛰️", "🚀", "🪐", "🌠", "☄️", "🌕", "🌖", "🌗", "🌘",
            "🏆", "🥇", "🥈", "🥉", "🎖️", "🏅", "🎗️", "💎", "👑", "⭐"
        ],
        "access": ["A", "B", "C"],
        "price": "₹499/month"
    }
}

# ============ DATABASE ============
user_tiers = {}
user_tier_expiry = {}
active_codes = {}
pending_purchases = {}
user_cooldowns = {}

# ============ LOGGING ============
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ============ SELF-PING ============
async def self_ping(context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=f"🔄 **Bot is Alive!**\n\n⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n🟢 Status: Active\n⏳ Next ping in: 10 minutes"
        )
        logger.info("Self-ping sent successfully")
    except Exception as e:
        logger.error(f"Self-ping failed: {e}")

# ============ HELPER FUNCTIONS ============
def generate_code(tier, duration_hours=24):
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    while code in active_codes:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    expiry_time = datetime.now() + timedelta(hours=duration_hours)
    active_codes[code] = {
        "tier": tier,
        "used": False,
        "generated_by": OWNER_ID,
        "expiry": expiry_time,
        "duration": duration_hours
    }
    return code, expiry_time

def get_available_emojis(user_id):
    user_id_str = str(user_id)
    if user_id_str in user_tier_expiry:
        if datetime.now() > user_tier_expiry[user_id_str]:
            if user_id_str in user_tiers:
                del user_tiers[user_id_str]
            if user_id_str in user_tier_expiry:
                del user_tier_expiry[user_id_str]
            return []
    tier = user_tiers.get(user_id_str)
    if not tier:
        return []
    all_emojis = []
    for t in ["A", "B", "C", "D"]:
        all_emojis.extend(TIERS[t]["emojis"])
        if t == tier:
            break
    return all_emojis

def get_tier_expiry_text(user_id):
    user_id_str = str(user_id)
    if user_id_str not in user_tier_expiry:
        return "❌ No active tier"
    remaining = user_tier_expiry[user_id_str] - datetime.now()
    if remaining.total_seconds() <= 0:
        return "❌ Expired"
    days = remaining.days
    hours = remaining.seconds // 3600
    minutes = (remaining.seconds % 3600) // 60
    if days > 0:
        return f"⏰ {days}d {hours}h remaining"
    elif hours > 0:
        return f"⏰ {hours}h {minutes}m remaining"
    else:
        return f"⏰ {minutes}m remaining"

def add_premium_emojis(text, user_id):
    emojis = get_available_emojis(user_id)
    if not emojis:
        return text
    words = text.split()
    if len(words) == 0:
        return text
    new_words = []
    tier = user_tiers.get(str(user_id))
    for word in words:
        if tier == "A":
            if random.random() < 0.3:
                new_words.append(f"{word} {random.choice(emojis)}")
            else:
                new_words.append(word)
        elif tier == "B":
            if random.random() < 0.4:
                new_words.append(f"{word} {random.choice(emojis)}")
            else:
                new_words.append(word)
        elif tier == "C":
            if random.random() < 0.5:
                emoji_count = 2 if random.random() < 0.2 else 1
                emojis_to_add = random.sample(emojis, min(emoji_count, len(emojis)))
                new_words.append(f"{word} {' '.join(emojis_to_add)}")
            else:
                new_words.append(word)
        else:  # Tier D
            if random.random() < 0.7:
                emoji_count = random.choice([1, 2, 3])
                emojis_to_add = random.sample(emojis, min(emoji_count, len(emojis)))
                new_words.append(f"{word} {' '.join(emojis_to_add)}")
            else:
                new_words.append(word)
    result = " ".join(new_words)
    if tier == "C":
        result = f"🌟 {result} 🌟"
    elif tier == "D":
        result = f"👑✨ {result} ✨👑"
    return result

# ============ COMMAND HANDLERS ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome_text = f"""
🌟✨🌈 **WELCOME TO ULTIMATE PREMIUM EMOJI BOT** 🌈✨🌟

👑 **Hello {user.first_name}!** 
💎 Your ultimate premium emoji experience starts now!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 **PREMIUM TIERS:**

🟢 **TIER A - BASIC** (FREE) - 70+ Emojis
🔵 **TIER B - SILVER** (₹99/month) - 80+ Emojis
🟡 **TIER C - GOLD** (₹199/month) - 90+ Emojis
🟣 **TIER D - PLATINUM** (₹499/month) - 100+ Emojis

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚡ **COMMANDS:**
/start - Welcome message
/status - Check your tier
/tiers - View all tiers
/buy - Purchase premium
/gen [tier] [time] - Generate code (Owner)
/redeem [code] - Redeem code
/help - Help menu
/expiry - Check expiry

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👑 **OWNER:** `{OWNER_ID}`

🌟✨ **ENJOY THE ULTIMATE PREMIUM EXPERIENCE!** ✨🌟
"""
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
⚡ **ULTIMATE PREMIUM EMOJI BOT - HELP** ⚡

📋 **ALL COMMANDS:**
/start - Welcome message
/status - Check your tier & expiry
/tiers - View all tier details
/buy - Purchase premium tier
/gen [tier] [time] - Generate code (Owner only)
/redeem [code] - Redeem a tier code
/help - Show this help message
/expiry - Check premium expiry time

⏰ **CODE TIME FORMATS:**
1h, 2h, 3h - Hours
1d, 2d, 3d - Days
1mo, 2mo - Months
1y, 2y - Years

👑 **Owner ID:** `{OWNER_ID}`
"""
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    tier = user_tiers.get(user_id)
    if tier:
        tier_info = TIERS[tier]
        emoji_count = len(get_available_emojis(user_id))
        expiry_text = get_tier_expiry_text(user_id)
        status_text = f"""
✨👑 **YOUR PREMIUM STATUS** 👑✨

👤 **User:** {update.effective_user.first_name}
{tier_info['color']} **Current Tier:** {tier_info['name']}
📊 **Emojis Available:** {emoji_count}/{tier_info['emoji_count']}
⏰ **Expiry:** {expiry_text}
🎯 **Access Level:** {'✅ ALL TIERS' if tier == 'D' else f'✅ Tier {tier} + below'}
"""
    else:
        status_text = """
⚠️ **No Premium Access**

You don't have any premium tier yet!

🎯 **Get Premium Access:**
1️⃣ /buy - Purchase premium
2️⃣ Contact owner for a code
3️⃣ /redeem [code] to redeem

👑 **Owner:** `{OWNER_ID}`
"""
    await update.message.reply_text(status_text, parse_mode='Markdown')

async def tiers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tiers_text = """
🌟👑 **PREMIUM TIERS** 👑🌟

🟢 **TIER A - BASIC** (FREE)
├─ 70+ Premium Emojis
└─ FREE for everyone!

🔵 **TIER B - SILVER** (₹99/month)
├─ Includes Tier A
├─ 80+ Premium Emojis
└─ More emoji variety

🟡 **TIER C - GOLD** (₹199/month)
├─ Includes A & B
├─ 90+ Premium Emojis
├─ Double emoji chance
└─ Special badge

🟣 **TIER D - PLATINUM** (₹499/month)
├─ Includes ALL tiers
├─ 100+ ALL Premium Emojis
├─ 3x More Emojis!
├─ Emojis on EVERY word
└─ Platinum badge

👑 **Owner:** `{OWNER_ID}`
"""
    await update.message.reply_text(tiers_text, parse_mode='Markdown')

async def gen_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        await update.message.reply_text("❌ **Unauthorized!** Only the owner can generate codes.", parse_mode='Markdown')
        return
    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ **Usage:** /gen [tier] [time]\n\n"
            "**Time formats:**\n"
            "1h, 2h, 3h - Hours\n"
            "1d, 2d, 3d - Days\n"
            "1mo, 2mo - Months\n"
            "1y, 2y - Years\n\n"
            "**Examples:**\n"
            "/gen D 1mo\n"
            "/gen B 7d\n"
            "/gen C 1y",
            parse_mode='Markdown'
        )
        return
    tier = context.args[0].upper()
    time_str = context.args[1].lower()
    if tier not in TIERS:
        await update.message.reply_text("❌ Invalid tier! Available: A, B, C, D", parse_mode='Markdown')
        return
    duration_hours = 0
    if time_str.endswith('h'):
        duration_hours = int(time_str[:-1])
    elif time_str.endswith('d'):
        duration_hours = int(time_str[:-1]) * 24
    elif time_str.endswith('mo'):
        duration_hours = int(time_str[:-2]) * 30 * 24
    elif time_str.endswith('y'):
        duration_hours = int(time_str[:-1]) * 365 * 24
    else:
        await update.message.reply_text("❌ Invalid time format! Use: 1h, 2d, 1mo, 1y", parse_mode='Markdown')
        return
    code, expiry_time = generate_code(tier, duration_hours)
    tier_name = TIERS[tier]['name']
    if duration_hours < 24:
        time_display = f"{duration_hours} hours"
    elif duration_hours < 720:
        time_display = f"{duration_hours // 24} days"
    elif duration_hours < 8760:
        time_display = f"{duration_hours // (30 * 24)} months"
    else:
        time_display = f"{duration_hours // (365 * 24)} years"
    message = f"""
✅ **CODE GENERATED SUCCESSFULLY!**

🎯 **Tier:** {tier_name}
⏰ **Duration:** {time_display}
🔑 **Code:** `{code}`
📅 **Expires:** {expiry_time.strftime('%Y-%m-%d %H:%M:%S')}

📤 **Share this code with user:**
/redeem {code}

⚠️ **Code expires after:** {time_display}
⚠️ **Single use only!**
"""
    await update.message.reply_text(message, parse_mode='Markdown')

async def redeem_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    username = update.effective_user.first_name
    if not context.args or len(context.args) < 1:
        await update.message.reply_text("❌ **Usage:** /redeem [code]\nExample: /redeem ABC12345", parse_mode='Markdown')
        return
    code = context.args[0].upper()
    if code not in active_codes:
        await update.message.reply_text("❌ **Invalid Code!** This code doesn't exist.", parse_mode='Markdown')
        return
    code_data = active_codes[code]
    if datetime.now() > code_data["expiry"]:
        await update.message.reply_text("❌ **Code Expired!** This code has expired.", parse_mode='Markdown')
        return
    if code_data["used"]:
        await update.message.reply_text("❌ **Already Used!** This code has been redeemed already.", parse_mode='Markdown')
        return
    tier = code_data["tier"]
    user_tiers[user_id] = tier
    user_tier_expiry[user_id] = code_data["expiry"]
    code_data["used"] = True
    code_data["used_by"] = user_id
    code_data["used_by_name"] = username
    tier_name = TIERS[tier]['name']
    emoji_count = len(get_available_emojis(int(user_id)))
    tier_info = TIERS[tier]
    await context.bot.send_message(
        chat_id=OWNER_ID,
        text=f"✅ **Code Redeemed!**\n\n👤 User: {username} (ID: {user_id})\n🎯 Tier: {tier_name}\n🔑 Code: {code}"
    )
    message = f"""
🎉 **TIER UPGRADE SUCCESSFUL!** 🎉

{tier_info['color']} **Tier:** {tier_name}
📊 **Emojis Available:** {emoji_count}
⏰ **Valid Until:** {code_data['expiry'].strftime('%Y-%m-%d %H:%M:%S')}

✨ **Your messages will now have premium emojis!**
💎 **Enjoy your premium experience!** 💎
"""
    await update.message.reply_text(message, parse_mode='Markdown')

async def buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [
            InlineKeyboardButton("🟢 Tier A - FREE", callback_data="buy_A"),
            InlineKeyboardButton("🔵 Tier B - ₹99/mo", callback_data="buy_B")
        ],
        [
            InlineKeyboardButton("🟡 Tier C - ₹199/mo", callback_data="buy_C"),
            InlineKeyboardButton("🟣 Tier D - ₹499/mo", callback_data="buy_D")
        ],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "💎 **SELECT YOUR PREMIUM TIER** 💎\n\n"
        "Choose the tier you want to purchase:\n\n"
        "🟢 **Tier A** - FREE (Already active)\n"
        "🔵 **Tier B** - ₹99/month\n"
        "🟡 **Tier C** - ₹199/month\n"
        "🟣 **Tier D** - ₹499/month",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = str(query.from_user.id)
    if data == "cancel":
        await query.edit_message_text("❌ Purchase cancelled.", parse_mode='Markdown')
        return
    if data.startswith("buy_"):
        tier = data.split("_")[1]
        if tier == "A":
            await query.edit_message_text(
                "✅ **Tier A is FREE!**\n\n"
                "You already have access to Tier A emojis!\n"
                "Just send any message and I'll add emojis for you! 😊",
                parse_mode='Markdown'
            )
        else:
            keyboard = [
                [InlineKeyboardButton("✅ Confirm Purchase", callback_data=f"confirm_{tier}")],
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(
                f"💳 **PURCHASE CONFIRMATION** 💳\n\n"
                f"📋 **Selected Tier:** {TIERS[tier]['name']}\n"
                f"💰 **Price:** {TIERS[tier]['price']}\n\n"
                f"⚠️ **Note:** Payment is manual. Contact owner to complete payment.\n"
                f"👑 **Owner:** @OwnerUsername\n\n"
                f"Click confirm to proceed:",
                reply_markup=reply_markup,
                parse_mode='Markdown'
            )
    elif data.startswith("confirm_"):
        tier = data.split("_")[1]
        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=f"💰 **New Purchase Request!** 💰\n\n"
                 f"👤 User: {query.from_user.first_name} (ID: {user_id})\n"
                 f"🎯 Tier: {TIERS[tier]['name']}\n"
                 f"⏰ Requested: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        await query.edit_message_text(
            f"✅ **Purchase Request Sent!** ✅\n\n"
            f"📋 **Tier:** {TIERS[tier]['name']}\n"
            f"💎 **Status:** Pending Payment\n\n"
            f"📧 **Next Steps:**\n"
            f"1. Contact owner for payment\n"
            f"2. Complete payment\n"
            f"3. Receive your code\n"
            f"4. Use /redeem [code]\n\n"
            f"👑 **Owner:** @OwnerUsername\n\n"
            f"Thank you for your interest! 💎",
            parse_mode='Markdown'
        )

async def expiry_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in user_tiers:
        await update.message.reply_text("⚠️ You don't have any active premium tier.", parse_mode='Markdown')
        return
    expiry_text = get_tier_expiry_text(user_id)
    tier = user_tiers[user_id]
    tier_name = TIERS[tier]['name']
    await update.message.reply_text(
        f"⏰ **PREMIUM EXPIRY** ⏰\n\n"
        f"👤 User: {update.effective_user.first_name}\n"
        f"🎯 Tier: {tier_name}\n"
        f"⏳ {expiry_text}\n\n"
        f"💎 Want to extend? Contact owner!",
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    if not text:
        return
    if user_id in user_cooldowns:
        if time.time() - user_cooldowns[user_id] < 1:
            return
    user_cooldowns[user_id] = time.time()
    premium_text = add_premium_emojis(text, user_id)
    if premium_text != text:
        if str(user_id) in user_tiers:
            await update.message.reply_text(premium_text)
        else:
            user_tiers[str(user_id)] = "A"
            user_tier_expiry[str(user_id)] = datetime.now() + timedelta(days=365)
            premium_text = add_premium_emojis(text, user_id)
            await update.message.reply_text(premium_text)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.warning(f"Update {update} caused error {context.error}")

# ============ MAIN FUNCTION ============
def main():
    """Start the bot"""
    application = Application.builder().token(TOKEN).build()
    
    # Command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("status", status))
    application.add_handler(CommandHandler("tiers", tiers))
    application.add_handler(CommandHandler("buy", buy_command))
    application.add_handler(CommandHandler("gen", gen_code))
    application.add_handler(CommandHandler("redeem", redeem_code))
    application.add_handler(CommandHandler("expiry", expiry_command))
    
    # Callback handler for buttons
    application.add_handler(CallbackQueryHandler(button_callback))
    
    # Message handler
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Error handler
    application.add_error_handler(error_handler)
    
    # Start the bot
    print("🚀 Bot is running...")
    print(f"👑 Owner ID: {OWNER_ID}")
    print("💎 Premium Emoji Bot started successfully!")
    
    # Self-ping job
    job_queue = application.job_queue
    if job_queue:
        job_queue.run_repeating(self_ping, interval=600, first=10)
        print("🔄 Self-ping scheduled (every 10 minutes)")
    
    # Start polling
    application.run_polling()

if __name__ == "__main__":
    main()
