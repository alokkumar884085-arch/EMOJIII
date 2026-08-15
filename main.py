import logging
import random
import string
import time
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
import asyncio
import re
import requests

# ============ CONFIGURATION ============
TOKEN = "8904097497:AAGazvlppLfBymhWP18Cjq7Hdi2XSc0DZvo"
OWNER_ID = 8785590284  # Owner's Telegram ID

# ============ 200+ PREMIUM EMOJIS BY TIER ============
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
user_tiers = {}  # user_id -> tier
user_tier_expiry = {}  # user_id -> expiry_time (datetime)
active_codes = {}  # code -> {"tier": "A", "used": False, "generated_by": owner_id, "expiry": datetime}
pending_purchases = {}  # user_id -> {"tier": "A", "timestamp": datetime}
user_cooldowns = {}  # user_id -> last_used_time

# ============ LOGGING ============
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ============ SELF-PING FUNCTION ============
async def self_ping(context: ContextTypes.DEFAULT_TYPE):
    """Automatic self-ping every 10 minutes"""
    try:
        # Send ping to owner
        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=f"🔄 **Bot is Alive!**\n\n"
                 f"⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                 f"🟢 Status: Active\n"
                 f"⏳ Next ping in: 10 minutes\n\n"
                 f"✅ All systems working properly!"
        )
        logger.info("Self-ping sent successfully")
    except Exception as e:
        logger.error(f"Self-ping failed: {e}")

# ============ HELPER FUNCTIONS ============
def generate_code(tier, duration_hours=24):
    """Generate a unique 10-character code for a tier with expiry"""
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
    """Get all emojis available for a user based on their tier and expiry"""
    user_id_str = str(user_id)
    
    # Check if tier is expired
    if user_id_str in user_tier_expiry:
        if datetime.now() > user_tier_expiry[user_id_str]:
            # Tier expired
            if user_id_str in user_tiers:
                del user_tiers[user_id_str]
            if user_id_str in user_tier_expiry:
                del user_tier_expiry[user_id_str]
            return []
    
    tier = user_tiers.get(user_id_str)
    if not tier:
        return []
    
    all_emojis = []
    # Add emojis from current tier and all lower tiers
    for t in ["A", "B", "C", "D"]:
        all_emojis.extend(TIERS[t]["emojis"])
        if t == tier:
            break
    
    return all_emojis

def get_tier_expiry_text(user_id):
    """Get remaining time for tier expiry"""
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

def add_premium_emojis(text, user_id, intensity=0.5):
    """Add premium emojis to text based on user's tier"""
    emojis = get_available_emojis(user_id)
    if not emojis:
        return text
    
    words = text.split()
    if len(words) == 0:
        return text
    
    new_words = []
    tier = user_tiers.get(str(user_id))
    
    for i, word in enumerate(words):
        # Different intensity based on tier
        if tier == "A":
            intensity = 0.3
            emoji_count = 1
        elif tier == "B":
            intensity = 0.4
            emoji_count = 1
        elif tier == "C":
            intensity = 0.5
            emoji_count = 2 if random.random() < 0.2 else 1
        else:  # Tier D
            intensity = 0.7
            emoji_count = random.choice([1, 2, 3])
        
        if random.random() < intensity:
            emojis_to_add = random.sample(emojis, min(emoji_count, len(emojis)))
            new_words.append(f"{word} {' '.join(emojis_to_add)}")
        else:
            new_words.append(word)
    
    # Add premium badges for higher tiers
    result = " ".join(new_words)
    if tier == "C":
        result = f"🌟 {result} 🌟"
    elif tier == "D":
        result = f"👑✨ {result} ✨👑"
    
    return result

# ============ WELCOME MESSAGE ============
async def welcome_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send beautiful welcome message with emojis"""
    user = update.effective_user
    welcome_text = f"""
🌟✨🌈 **WELCOME TO ULTIMATE PREMIUM EMOJI BOT** 🌈✨🌟

👑 **Hello {user.first_name}!** 
💎 Your ultimate premium emoji experience starts now!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **WHAT I CAN DO:**
├─ ✨ Add 200+ premium emojis to your messages
├─ 💎 Tier-based emoji access system
├─ 👑 Special emojis for VIP users
├─ 🎯 Auto-emojify your texts
├─ ⏰ Time-based premium access
├─ 🛒 Purchase premium tiers
└─ 🚀 Much more!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 **PREMIUM TIERS:**

🟢 **TIER A - BASIC** (FREE)
├─ ✨ 70+ Basic Premium Emojis
├─ 🎯 Random emoji addition
└─ 💰 COMPLETELY FREE!

🔵 **TIER B - SILVER** (₹99/month)
├─ 🔹 Includes Tier A (✅)
├─ 💎 80+ Premium Silver Emojis
├─ 🌟 More emoji variety
└─ 🎯 Higher emoji frequency

🟡 **TIER C - GOLD** (₹199/month)
├─ 🟡 Includes Tier A & B (✅✅)
├─ 🌠 90+ Exclusive Gold Emojis
├─ 🎆 Double emoji chance
└─ 🏰 Special badges on messages

🟣 **TIER D - PLATINUM** (₹499/month)
├─ 🟣 Includes ALL TIERS (✅✅✅)
├─ 👑 100+ All Premium Emojis
├─ 💫 3x More Emojis!
├─ ✨ Emojis on EVERY word
├─ 👑 Special platinum badge
└─ 🏆 ULTIMATE EXPERIENCE!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⚡ **COMMANDS:**
├─ /start - Show this message
├─ /status - Check your current tier
├─ /tiers - View all tier details
├─ /buy - Purchase premium tier
├─ /gen [tier] [time] - Generate a code (Owner only)
├─ /redeem [code] - Redeem a tier code
├─ /help - Show all commands
└─ /expiry - Check premium expiry

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 **CODE TIME FORMATS:**
├─ 1h, 2h, 3h - Hours
├─ 1d, 2d, 3d - Days
├─ 1mo, 2mo, 3mo - Months
├─ 1y, 2y, 3y - Years
└─ Example: /gen D 1mo

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💎 **HOW TO GET PREMIUM:**
1️⃣ FREE - Use /status to check current tier
2️⃣ CODE - Get a code from owner
3️⃣ PURCHASE - Use /buy to get premium
4️⃣ REDEEM - /redeem [code]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👑 **OWNER:** `{OWNER_ID}`

📧 Contact owner for premium codes!

🌟✨ **ENJOY THE ULTIMATE PREMIUM EXPERIENCE!** ✨🌟
"""
    await update.message.reply_text(welcome_text, parse_mode='Markdown')

# ============ COMMAND HANDLERS ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await welcome_message(update, context)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
⚡ **ULTIMATE PREMIUM EMOJI BOT - HELP** ⚡

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📋 **ALL COMMANDS:**

/start - Show welcome message
/status - Check your current tier & expiry
/tiers - View all tier details
/buy - Purchase premium tier
/gen [tier] [time] - Generate a code (Owner only)
/redeem [code] - Redeem a tier code
/help - Show this help message
/expiry - Check premium expiry time

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **TIER DETAILS:**

🟢 **TIER A** (Basic - FREE)
├─ 70+ Premium Emojis
├─ Random emoji addition
└─ FREE for everyone!

🔵 **TIER B** (Silver - ₹99/mo)
├─ 80+ Premium Emojis
├─ Includes Tier A
└─ More emoji variety

🟡 **TIER C** (Gold - ₹199/mo)
├─ 90+ Premium Emojis
├─ Includes A & B
├─ Double emoji chance
└─ Special badge

🟣 **TIER D** (Platinum - ₹499/mo)
├─ 100+ ALL Premium Emojis
├─ Includes ALL tiers
├─ 3x More Emojis!
├─ Emojis on EVERY word
└─ Platinum badge

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

⏰ **CODE TIME FORMATS:**
├─ 1h = 1 Hour
├─ 1d = 1 Day  
├─ 1mo = 1 Month
├─ 1y = 1 Year
└─ Use: /gen D 1mo

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💎 **PURCHASE PREMIUM:**
1. Use /buy command
2. Select your tier
3. Choose duration
4. Complete payment
5. Get premium instantly!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔐 **OWNER ONLY:**
/gen A 1d - Tier A for 1 day
/gen B 1mo - Tier B for 1 month
/gen C 1y - Tier C for 1 year
/gen D 7d - Tier D for 7 days

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

👑 **Owner ID:** `{OWNER_ID}`

📧 Contact owner for premium access!
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
🆔 **ID:** `{user_id}`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{tier_info['color']} **Current Tier:** {tier_info['name']}

📊 **Emojis Available:** {emoji_count}/{tier_info['emoji_count']}

⏰ **Expiry:** {expiry_text}

🎯 **Access Level:** {'✅ ALL TIERS' if tier == 'D' else f'✅ Tier {tier} + below'}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💎 **Want higher tier?**
├─ /buy - Purchase premium
└─ Contact owner for codes!

👑 **Owner:** `{OWNER_ID}`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🌟 **Keep enjoying premium emojis!** 🌟
"""
    else:
        status_text = """
⚠️ **No Premium Access**

You don't have any premium tier yet!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **Get Premium Access:**

1️⃣ /buy - Purchase premium
2️⃣ Contact owner for a code
3️⃣ /redeem [code] to redeem

💰 **Tier Prices:**
├─ Tier B: ₹99/month
├─ Tier C: ₹199/month
└─ Tier D: ₹499/month

👑 **Owner:** `{OWNER_ID}`

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎁 **Try FREE Tier A!**
All users automatically get Tier A!
"""
    await update.message.reply_text(status_text, parse_mode='Markdown')

async def tiers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    tiers_text = """
🌟👑 **PREMIUM TIERS - COMPLETE DETAILS** 👑🌟

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🟢 **TIER A - BASIC PREMIUM** (FREE)
├─ 70+ Basic Premium Emojis
├─ ✨ Sparkle & Stars
├─ 🌸 Nature & Animals
├─ ☀️ Sky & Ocean
└─ 💰 COMPLETELY FREE!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔵 **TIER B - SILVER PREMIUM** (₹99/month)
├─ ✅ Includes Tier A
├─ 80+ Premium Silver Emojis
├─ 💎 Gems & Jewels
├─ 💻 Technology & Gadgets
├─ 🎵 Music & Entertainment
└─ 🎯 More emoji variety

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🟡 **TIER C - GOLD PREMIUM** (₹199/month)
├─ ✅✅ Includes Tier A & B
├─ 90+ Exclusive Gold Emojis
├─ 🌠 Space & Universe
├─ 🏛️ Architecture & Landmarks
├─ 🎊 Festivals & Celebrations
├─ 🎆 Double emoji chance
└─ 🌟 Special gold badge

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🟣 **TIER D - PLATINUM PREMIUM** (₹499/month)
├─ ✅✅✅ Includes ALL TIERS
├─ 100+ ULTIMATE Emojis
├─ 👑 Royal Platinum Collection
├─ 🚀 Space Ultimate
├─ 🏆 All Sports & Badges
├─ 💫 3x More Emojis!
├─ ✨ Emojis on EVERY word
├─ 👑 Special platinum badge
└─ 🏆 ULTIMATE EXPERIENCE!

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

💎 **UPGRADE NOW!**
├─ /buy - Purchase premium
├─ /redeem [code] - Redeem code
└─ Contact owner for special offers!

👑 **Owner:** `{OWNER_ID}`

🌟 **Choose your tier today!** 🌟
"""
    await update.message.reply_text(tiers_text, parse_mode='Markdown')

async def gen_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate a tier code with time (Owner only)"""
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
    
    # Parse time
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
    
    # Format expiry time
    if duration_hours < 24:
        time_display = f"{duration_hours} hours"
    elif duration_hours < 720:  # 30 days
        time_display = f"{duration_hours // 24} days"
    elif duration_hours < 8760:  # 365 days
        time_display = f"{duration_hours // (30 * 24)} months"
    else:
        time_display = f"{duration_hours // (365 * 24)} years"
    
    message = f"""
✅ **CODE GENERATED SUCCESSFULLY!**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 **Tier:** {tier_name}
⏰ **Duration:** {time_display}
🔑 **Code:** `{code}`
📅 **Expires:** {expiry_time.strftime('%Y-%m-%d %H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📤 **Share this code with user:**
/redeem {code}

⚠️ **Code expires after:** {time_display}
⚠️ **Single use only!**

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📧 **User will receive expiry notification!**
"""
    await update.message.reply_text(message, parse_mode='Markdown')

async def redeem_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Redeem a tier code"""
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
    
    # Check expiry
    if datetime.now() > code_data["expiry"]:
        await update.message.reply_text("❌ **Code Expired!** This code has expired.", parse_mode='Markdown')
        return
    
    if code_data["used"]:
        await update.message.reply_text("❌ **Already Used!** This code has been redeemed already.", parse_mode='Markdown')
        return
    
    # Redeem the code
    tier = code_data["tier"]
    user_tiers[user_id] = tier
    user_tier_expiry[user_id] = code_data["expiry"]
    code_data["used"] = True
    code_data["used_by"] = user_id
    code_data["used_by_name"] = username
    
    tier_name = TIERS[tier]['name']
    emoji_count = len(get_available_emojis(int(user_id)))
    
    # Send notification to owner
    await context.bot.send_message(
        chat_id=OWNER_ID,
        text=f"✅ **Code Redeemed!**\n\n"
             f"👤 User: {username} (ID: {user_id})\n"
             f"🎯 Tier: {tier_name}\n"
             f"🔑 Code: {code}"
    )
    
    message = f"""
🎉 **TIER UPGRADE SUCCESSFUL!** 🎉

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

{tier_info['color']} **Tier:** {tier_name}

📊 **Emojis Available:** {emoji_count}

⏰ **Valid Until:** {code_data['expiry'].strftime('%Y-%m-%d %H:%M:%S')}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✨ **Your messages will now have premium emojis!**

📧 **You'll be notified when premium expires.**

💎 **Enjoy your premium experience!** 💎
"""
    await update.message.reply_text(message, parse_mode='Markdown')

async def buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Purchase premium tier"""
    keyboard = [
        [
            InlineKeyboardButton("🟢 Tier A - FREE", callback_data="buy_A_1mo"),
            InlineKeyboardButton("🔵 Tier B - ₹99/mo", callback_data="buy_B_1mo")
        ],
        [
            InlineKeyboardButton("🟡 Tier C - ₹199/mo", callback_data="buy_C_1mo"),
            InlineKeyboardButton("🟣 Tier D - ₹499/mo", callback_data="buy_D_1mo")
        ],
        [
            InlineKeyboardButton("📅 1 Month", callback_data="duration_1mo"),
            InlineKeyboardButton("📅 3 Months (10% off)", callback_data="duration_3mo"),
            InlineKeyboardButton("📅 6 Months (20% off)", callback_data="duration_6mo"),
            InlineKeyboardButton("📅 1 Year (30% off)", callback_data="duration_1y")
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
        "🟣 **Tier D** - ₹499/month\n\n"
        "Select duration below 👇",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle button presses"""
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
            # Store pending purchase
            pending_purchases[user_id] = {"tier": tier, "timestamp": datetime.now()}
            
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
        
        # Notify owner about purchase request
        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=f"💰 **New Purchase Request!** 💰\n\n"
                 f"👤 User: {query.from_user.first_name} (ID: {user_id})\n"
                 f"🎯 Tier: {TIERS[tier]['name']}\n"
                 f"⏰ Requested: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                 f"Contact user to complete payment."
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
    
    elif data.startswith("duration_"):
        duration = data.split("_")[1]
        # This is for the duration selection in buy command
        await query.edit_message_text(
            f"📅 **Duration Selected:** {duration}\n\n"
            f"Please select a tier first using the main menu.\n"
            f"Use /buy to start again.",
            parse_mode='Markdown'
        )

async def expiry_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check premium expiry time"""
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

# ============ MESSAGE HANDLER ============
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Process messages and add premium emojis"""
    user_id = update.effective_user.id
    text = update.message.text
    
    if not text:
        return
    
    # Check cooldown (prevent spam)
    if user_id in user_cooldowns:
        if time.time() - user_cooldowns[user_id] < 1:  # 1 second cooldown
            return
    
    user_cooldowns[user_id] = time.time()
    
    # Add premium emojis
    premium_text = add_premium_emojis(text, user_id)
    
    if premium_text != text:
        # Check if user has premium
        if str(user_id) in user_tiers:
            await update.message.reply_text(premium_text)
        else:
            # Give FREE Tier A to all users
            user_tiers[str(user_id)] = "A"
            # Set expiry to 1 year for free tier
            user_tier_expiry[str(user_id)] = datetime.now() + timedelta(days=365)
            premium_text = add_premium_emojis(text, user_id)
            await update.message.reply_text(premium_text)

# ============ ERROR HANDLER ============
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
    
    # ============ SELF-PING JOB ============
    job_queue = application.job_queue
    if job_queue:
        # Schedule self-ping every 10 minutes (600 seconds)
        job_queue.run_repeating(self_ping, interval=600, first=10)
        print("🔄 Self-ping scheduled (every 10 minutes)")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
