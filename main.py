import logging
import random
import string
import time
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# ============ CONFIGURATION ============
TOKEN = "8904097497:AAGazvlppLfBymhWP18Cjq7Hdi2XSc0DZvo"
OWNER_ID = 8785590284

# ============ TELEGRAM PREMIUM EMOJIS ============
# Ye Official Telegram Premium Emojis hain jo sirf Premium users ko available hain

TELEGRAM_PREMIUM_EMOJIS = [
    # Stars & Sparkles (Premium)
    "✨", "⭐", "🌟", "💫", "🌠", "☄️", 
    # Hearts & Love (Premium)
    "💖", "💗", "💝", "💞", "💕", "💘", "💟", "❣️",
    # Crown & Royal (Premium)
    "👑", "💎", "🏆", "🥇", "🎖️",
    # Glowing & Shiny (Premium)
    "🔥", "⚡", "💥", "🌈", "🎆", "🎇", "✨",
    # Special Animals (Premium)
    "🦄", "🐉", "🦋", "🐝", "🐞",
    # Special Nature (Premium)
    "🌸", "🌺", "🌹", "🌷", "🌻", "🌼", "💐",
    # Tech & Gadgets (Premium)
    "💻", "🖥️", "⌨️", "📱", "📲", "💡", "🔮",
    # Music & Entertainment (Premium)
    "🎵", "🎶", "🎼", "🎹", "🎧", "🎤", "🎭", "🎪", "🎨", "🎬",
    # Sports (Premium)
    "⚽", "🏀", "🏈", "⚾", "🎾", "🏐", "🎱", "🎳",
    # Space (Premium)
    "🪐", "🚀", "🛸", "👽", "🤖", "👾",
    # Festivals (Premium)
    "🎊", "🎉", "🎈", "🎀", "🎁", "🎄", "🎃",
    # Special Badges (Premium)
    "🏅", "🎗️", "📿", "🧿", "🔯", "🕎", "☯️", "☮️",
    # Extra Premium (Telegram Exclusive)
    "💠", "🔮", "💜", "💙", "💚", "💛", "🧡", "❤️", "🖤", "🤍", "🤎"
]

# ============ TIERS WITH TELEGRAM PREMIUM EMOJIS ============
TIERS = {
    "A": {
        "name": "✨ BASIC PREMIUM",
        "color": "🟢",
        "emojis": TELEGRAM_PREMIUM_EMOJIS[:40],  # First 40 premium emojis
        "access": [],
        "price": "FREE"
    },
    "B": {
        "name": "💎 SILVER PREMIUM",
        "color": "🔵",
        "emojis": TELEGRAM_PREMIUM_EMOJIS[:70],  # First 70 premium emojis
        "access": ["A"],
        "price": "₹99/month"
    },
    "C": {
        "name": "🌟 GOLD PREMIUM",
        "color": "🟡",
        "emojis": TELEGRAM_PREMIUM_EMOJIS,  # All premium emojis
        "access": ["A", "B"],
        "price": "₹199/month"
    },
    "D": {
        "name": "👑 PLATINUM PREMIUM",
        "color": "🟣",
        "emojis": TELEGRAM_PREMIUM_EMOJIS * 2,  # Double emojis for more variety
        "access": ["A", "B", "C"],
        "price": "₹499/month"
    }
}

# ============ DATABASE ============
user_tiers = {}
user_tier_expiry = {}
active_codes = {}
user_cooldowns = {}

# ============ LOGGING ============
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ============ SELF-PING ============
async def self_ping(context: ContextTypes.DEFAULT_TYPE):
    try:
        await context.bot.send_message(
            chat_id=OWNER_ID,
            text=f"🔄 **Bot is Alive!**\n\n⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n🟢 Status: Active\n💎 Using Telegram Premium Emojis!"
        )
    except Exception as e:
        logger.error(f"Self-ping failed: {e}")

# ============ HELPER FUNCTIONS ============
def generate_code(tier, duration_hours=24):
    code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    while code in active_codes:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    expiry_time = datetime.now() + timedelta(hours=duration_hours)
    active_codes[code] = {"tier": tier, "used": False, "expiry": expiry_time}
    return code, expiry_time

def get_available_emojis(user_id):
    user_id_str = str(user_id)
    if user_id_str in user_tier_expiry:
        if datetime.now() > user_tier_expiry[user_id_str]:
            user_tiers.pop(user_id_str, None)
            user_tier_expiry.pop(user_id_str, None)
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
    if not words:
        return text
    new_words = []
    tier = user_tiers.get(str(user_id))
    for word in words:
        if tier == "A" and random.random() < 0.3:
            new_words.append(f"{word} {random.choice(emojis)}")
        elif tier == "B" and random.random() < 0.4:
            new_words.append(f"{word} {random.choice(emojis)}")
        elif tier == "C" and random.random() < 0.5:
            count = 2 if random.random() < 0.2 else 1
            emojis_to_add = random.sample(emojis, min(count, len(emojis)))
            new_words.append(f"{word} {' '.join(emojis_to_add)}")
        elif tier == "D" and random.random() < 0.7:
            count = random.choice([1, 2, 3])
            emojis_to_add = random.sample(emojis, min(count, len(emojis)))
            new_words.append(f"{word} {' '.join(emojis_to_add)}")
        else:
            new_words.append(word)
    result = " ".join(new_words)
    if tier == "C":
        return f"🌟✨ {result} ✨🌟"
    elif tier == "D":
        return f"👑✨💎 {result} 💎✨👑"
    return result

# ============ COMMAND HANDLERS ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"🌟✨💎 **WELCOME TO PREMIUM EMOJI BOT** 💎✨🌟\n\n"
        f"👑 **Hello {user.first_name}!**\n"
        f"💎 **Telegram Premium Emojis** available!\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"📋 **COMMANDS:**\n"
        f"/start - Welcome ✨\n"
        f"/status - Check tier 💎\n"
        f"/tiers - View tiers 🌟\n"
        f"/buy - Purchase premium 💰\n"
        f"/redeem [code] - Redeem code 🔑\n"
        f"/help - Help ℹ️\n"
        f"/expiry - Check expiry ⏰\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💎 **Premium Emojis Included:**\n"
        f"✨⭐🌟💫🌠☄️💖💗💝👑💎🏆🔥⚡🌈🦄🐉🌸🌺🌹\n\n"
        f"👑 **Owner:** `{OWNER_ID}`",
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚡ **PREMIUM EMOJI BOT - HELP** ⚡\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "📋 **COMMANDS:**\n"
        "/start - Welcome message ✨\n"
        "/status - Check your tier 💎\n"
        "/tiers - View all tiers 🌟\n"
        "/buy - Purchase premium 💰\n"
        "/redeem [code] - Redeem code 🔑\n"
        "/help - This message ℹ️\n"
        "/expiry - Check expiry ⏰\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "💎 **Telegram Premium Emojis:**\n"
        "✨⭐🌟💫🌠☄️💖💗💝👑💎🏆\n"
        "🔥⚡🌈🦄🐉🌸🌺🌹💐🎆🎇\n\n"
        "👑 **Owner:** `{}`\n\n"
        "💎 **Enjoy Premium Emojis!** 💎".format(OWNER_ID),
        parse_mode='Markdown'
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    tier = user_tiers.get(user_id)
    if tier:
        tier_info = TIERS[tier]
        emoji_count = len(get_available_emojis(user_id))
        await update.message.reply_text(
            f"✨💎 **YOUR PREMIUM STATUS** 💎✨\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 **User:** {update.effective_user.first_name}\n"
            f"{tier_info['color']} **Tier:** {tier_info['name']}\n"
            f"📊 **Emojis:** {emoji_count} Premium Emojis\n"
            f"⏰ **Expiry:** {get_tier_expiry_text(user_id)}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"💎 **Telegram Premium Emojis Active!** ✨",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "⚠️ **No Premium Tier Active**\n\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            "🎯 **Get Premium Access:**\n"
            "1️⃣ /buy - Purchase premium\n"
            "2️⃣ Contact owner for code\n"
            "3️⃣ /redeem [code] to redeem\n\n"
            f"👑 **Owner:** `{OWNER_ID}`\n\n"
            "💎 **Get Telegram Premium Emojis Today!** ✨",
            parse_mode='Markdown'
        )

async def tiers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌟💎 **PREMIUM TIERS** 💎🌟\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🟢 **TIER A - BASIC** (FREE)\n"
        "├─ 40+ Telegram Premium Emojis\n"
        "└─ FREE for everyone! ✨\n\n"
        "🔵 **TIER B - SILVER** (₹99/mo)\n"
        "├─ 70+ Telegram Premium Emojis\n"
        "├─ Includes Tier A\n"
        "└─ More variety 💎\n\n"
        "🟡 **TIER C - GOLD** (₹199/mo)\n"
        "├─ 100+ Telegram Premium Emojis\n"
        "├─ Includes A & B\n"
        "├─ Double emoji chance\n"
        "└─ Special badge 🌟\n\n"
        "🟣 **TIER D - PLATINUM** (₹499/mo)\n"
        "├─ ALL Telegram Premium Emojis\n"
        "├─ Includes ALL tiers\n"
        "├─ 3x More Emojis! ✨\n"
        "├─ Emojis on EVERY word\n"
        "└─ Platinum badge 👑\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "💎 **All emojis are Telegram Premium!** \n"
        f"👑 **Owner:** `{OWNER_ID}`",
        parse_mode='Markdown'
    )

async def gen_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ **Unauthorized!** Only owner can generate codes.", parse_mode='Markdown')
        return
    if len(context.args) < 2:
        await update.message.reply_text(
            "❌ **Usage:** /gen [A/B/C/D] [time]\n\n"
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
        await update.message.reply_text("❌ Invalid tier! Use: A, B, C, D", parse_mode='Markdown')
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
        await update.message.reply_text("❌ Invalid time! Use: 1h, 2d, 1mo, 1y", parse_mode='Markdown')
        return
    code, expiry = generate_code(tier, duration_hours)
    tier_name = TIERS[tier]['name']
    await update.message.reply_text(
        f"✅ **CODE GENERATED!** ✅\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🎯 **Tier:** {tier_name}\n"
        f"🔑 **Code:** `{code}`\n"
        f"⏰ **Expires:** {expiry.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"📤 **Share with user:**\n"
        f"/redeem {code}\n\n"
        f"⚠️ **Single use only!**",
        parse_mode='Markdown'
    )

async def redeem_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if not context.args:
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
        await update.message.reply_text("❌ **Already Used!** This code has been redeemed.", parse_mode='Markdown')
        return
    tier = code_data["tier"]
    user_tiers[user_id] = tier
    user_tier_expiry[user_id] = code_data["expiry"]
    code_data["used"] = True
    tier_name = TIERS[tier]['name']
    emoji_count = len(get_available_emojis(int(user_id)))
    
    # Notify owner
    await context.bot.send_message(
        OWNER_ID,
        f"✅ **Code Redeemed!**\n\n👤 {update.effective_user.first_name}\n🎯 {tier_name}\n🔑 {code}"
    )
    
    await update.message.reply_text(
        f"🎉 **TIER UPGRADED!** 🎉\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"💎 **Tier:** {tier_name}\n"
        f"📊 **Emojis:** {emoji_count} Premium Emojis\n"
        f"⏰ **Valid until:** {code_data['expiry'].strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        f"✨ **Telegram Premium Emojis Activated!** ✨",
        parse_mode='Markdown'
    )

async def buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🟢 Tier A - FREE (40+ Emojis)", callback_data="buy_A")],
        [InlineKeyboardButton("🔵 Tier B - ₹99/mo (70+ Emojis)", callback_data="buy_B")],
        [InlineKeyboardButton("🟡 Tier C - ₹199/mo (100+ Emojis)", callback_data="buy_C")],
        [InlineKeyboardButton("🟣 Tier D - ₹499/mo (All Emojis)", callback_data="buy_D")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ]
    await update.message.reply_text(
        "💎 **SELECT YOUR PREMIUM TIER** 💎\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🟢 **Tier A** - 40+ Premium Emojis (FREE)\n"
        "🔵 **Tier B** - 70+ Premium Emojis (₹99/mo)\n"
        "🟡 **Tier C** - 100+ Premium Emojis (₹199/mo)\n"
        "🟣 **Tier D** - ALL Premium Emojis (₹499/mo)\n\n"
        "✨ **All emojis are Telegram Premium!**",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "cancel":
        await query.edit_message_text("❌ **Cancelled.**", parse_mode='Markdown')
        return
    if data.startswith("buy_"):
        tier = data.split("_")[1]
        if tier == "A":
            await query.edit_message_text(
                "✅ **Tier A is FREE!**\n\n"
                "✨ You now have access to 40+ Telegram Premium Emojis!\n"
                "💎 Just send any message to see them in action!",
                parse_mode='Markdown'
            )
            # Auto-assign Tier A
            user_id = str(query.from_user.id)
            user_tiers[user_id] = "A"
            user_tier_expiry[user_id] = datetime.now() + timedelta(days=365)
        else:
            keyboard = [
                [InlineKeyboardButton("✅ Confirm Purchase", callback_data=f"confirm_{tier}")],
                [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
            ]
            await query.edit_message_text(
                f"💳 **PURCHASE CONFIRMATION** 💳\n\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📋 **Tier:** {TIERS[tier]['name']}\n"
                f"💰 **Price:** {TIERS[tier]['price']}\n"
                f"💎 **Emojis:** {len(TIERS[tier]['emojis'])} Premium Emojis\n\n"
                f"⚠️ **Payment is manual.**\n"
                f"👑 **Contact owner:** @OwnerUsername\n\n"
                f"Click confirm to proceed:",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
    elif data.startswith("confirm_"):
        tier = data.split("_")[1]
        user_id = query.from_user.id
        user_name = query.from_user.first_name
        
        # Notify owner
        await context.bot.send_message(
            OWNER_ID,
            f"💰 **NEW PURCHASE REQUEST!** 💰\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👤 **User:** {user_name} (ID: {user_id})\n"
            f"🎯 **Tier:** {TIERS[tier]['name']}\n"
            f"💰 **Price:** {TIERS[tier]['price']}\n"
            f"⏰ **Time:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
            f"📧 **Contact user to complete payment.**"
        )
        
        await query.edit_message_text(
            f"✅ **PURCHASE REQUEST SENT!** ✅\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📋 **Tier:** {TIERS[tier]['name']}\n"
            f"💎 **Status:** Pending Payment\n\n"
            f"📧 **Next Steps:**\n"
            f"1️⃣ Contact owner for payment\n"
            f"2️⃣ Complete payment\n"
            f"3️⃣ Receive your code\n"
            f"4️⃣ Use /redeem [code]\n\n"
            f"👑 **Owner:** @OwnerUsername\n\n"
            f"💎 **Thank you for your interest!** ✨",
            parse_mode='Markdown'
        )

async def expiry_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in user_tiers:
        await update.message.reply_text(
            "⚠️ **No active premium tier.**\n\n"
            "Use /buy to purchase or /redeem [code] to redeem.",
            parse_mode='Markdown'
        )
        return
    tier = user_tiers[user_id]
    tier_name = TIERS[tier]['name']
    expiry_text = get_tier_expiry_text(user_id)
    await update.message.reply_text(
        f"⏰ **PREMIUM EXPIRY** ⏰\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👤 **User:** {update.effective_user.first_name}\n"
        f"💎 **Tier:** {tier_name}\n"
        f"⏳ {expiry_text}\n\n"
        f"💎 Want to extend? Contact owner!",
        parse_mode='Markdown'
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    if not text:
        return
    if user_id in user_cooldowns and time.time() - user_cooldowns[user_id] < 1:
        return
    user_cooldowns[user_id] = time.time()
    if str(user_id) not in user_tiers:
        user_tiers[str(user_id)] = "A"
        user_tier_expiry[str(user_id)] = datetime.now() + timedelta(days=365)
    premium_text = add_premium_emojis(text, user_id)
    if premium_text != text:
        await update.message.reply_text(premium_text)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")

# ============ MAIN ============
def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("tiers", tiers))
    app.add_handler(CommandHandler("buy", buy_command))
    app.add_handler(CommandHandler("gen", gen_code))
    app.add_handler(CommandHandler("redeem", redeem_code))
    app.add_handler(CommandHandler("expiry", expiry_command))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_error_handler(error_handler)
    
    if app.job_queue:
        app.job_queue.run_repeating(self_ping, interval=600, first=10)
        print("🔄 Self-ping scheduled (every 10 minutes)")
    
    print("🚀 Bot started with Telegram Premium Emojis!")
    print(f"👑 Owner ID: {OWNER_ID}")
    print(f"💎 Total Premium Emojis: {len(TELEGRAM_PREMIUM_EMOJIS)}")
    app.run_polling()

if __name__ == "__main__":
    main()
