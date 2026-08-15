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

# ============ TIERS WITH EMOJIS ============
TIERS = {
    "A": {
        "name": "✨ BASIC PREMIUM",
        "color": "🟢",
        "emojis": ["✨", "⭐", "🌟", "💫", "🔥", "🌈", "🎯", "🌸", "🌺", "🌹", "🌷", "🌻", "🌼", "💐", "🌿", "🌱", "🌳", "🌴", "🌵", "🍀", "☘️", "🍃", "🍂", "🍁", "☀️", "🌤️", "⛅", "🌥️", "☁️", "🌦️", "🌧️", "⛈️", "🌨️", "❄️", "☃️", "⛄", "💨", "🌫️", "🌬️", "🪐", "🌍", "🌎", "🌏", "🌕", "🦋", "🐝", "🐞", "🦄", "🐉", "🦁", "🐯", "🐺", "🐻", "🐼", "🐨", "🦊", "🐰", "🐭", "🐹", "🐱", "🐶", "🐠", "🐟", "🐬", "🐳", "🐋", "🦈", "🐙", "🦑", "🐚", "🌊"],
        "access": [],
        "price": "FREE"
    },
    "B": {
        "name": "💎 SILVER PREMIUM",
        "color": "🔵",
        "emojis": ["💎", "👑", "🏆", "🥇", "🥈", "🥉", "🎖️", "💠", "🔮", "💜", "💙", "💚", "💛", "🧡", "❤️", "🖤", "🤍", "🤎", "💗", "💖", "💝", "💞", "💕", "❣️", "💋", "💘", "💟", "💻", "🖥️", "⌨️", "🖱️", "🖨️", "📱", "📲", "☎️", "📞", "📟", "📠", "🔋", "🪫", "🔌", "💡", "🔦", "🕯️", "💸", "💵", "💶", "💷", "💴", "💰", "🪙", "💳", "🧾", "📊", "📈", "🎵", "🎶", "🎼", "🎹", "🥁", "🎷", "🎺", "🎸", "🎻", "🎧", "🎤", "🎭", "🎪", "🎨", "🎬", "🎮", "🕹️", "🎲", "🎯", "🎱", "⚽", "🏀", "🏈", "⚾", "🎾", "🏐", "🏉"],
        "access": ["A"],
        "price": "₹99/month"
    },
    "C": {
        "name": "🌟 GOLD PREMIUM",
        "color": "🟡",
        "emojis": ["🌟", "⭐", "🌠", "☀️", "🌈", "🎆", "🎇", "🌅", "🌄", "🎠", "🎢", "🎡", "🏰", "🗼", "🎑", "🌉", "🌌", "🌊", "🌋", "🗻", "🪐", "☄️", "💫", "⭐", "🌟", "✨", "⚡", "🔥", "💥", "🎯", "🚀", "🛸", "👽", "🤖", "👾", "🧠", "💡", "🔮", "🧬", "⚗️", "🏛️", "⛩️", "🕍", "⛪", "🕌", "🛕", "🕋", "🗽", "🗿", "🏗️", "🎊", "🎉", "🎈", "🎀", "🎁", "🎄", "🎃", "🎐", "🏮", "🧨", "🪅", "🎆", "🎇", "🪩", "🎭", "🎪", "🎨", "🎬", "🎤", "💎", "👑", "💰", "💳", "🪙", "💸", "💵", "💶", "💷", "💴", "📿", "🧿", "🔯", "🕎", "☯️", "☮️", "✝️", "☪️", "🕉️", "☸️"],
        "access": ["A", "B"],
        "price": "₹199/month"
    },
    "D": {
        "name": "👑 PLATINUM PREMIUM",
        "color": "🟣",
        "emojis": ["👑", "💎", "⭐", "🌟", "✨", "🔥", "💫", "🌈", "🎆", "🎇", "🌠", "💠", "🔮", "💜", "💙", "💚", "💛", "🧡", "❤️", "🖤", "🤍", "💝", "💖", "💗", "💓", "💞", "💕", "❣️", "💋", "💘", "💟", "🩷", "🩵", "🩶", "🩹", "💉", "💊", "🩺", "📿", "🧿", "🖥️", "⌨️", "🖱️", "🖨️", "📱", "📲", "☎️", "📞", "📟", "📠", "🔋", "🪫", "🔌", "💡", "🔦", "🕯️", "🧯", "🛢️", "💸", "💵", "💶", "💷", "💴", "💰", "🪙", "💳", "🧾", "📊", "📈", "📉", "⚽", "🏀", "🏈", "⚾", "🎾", "🏐", "🏉", "🎱", "🎳", "🏏", "🏑", "🏒", "🥅", "⛳", "🏌️", "🏄", "🏊", "🤽", "🧗", "🚴", "🚵", "🏇", "⛸️", "🏂", "⛷️", "🎿", "🏋️", "🤼", "🤸", "🤾", "🪐", "☄️", "💫", "⭐", "🌟", "✨", "⚡", "🔥", "💥", "🎯", "🚀", "🛸", "👽", "🤖", "👾", "🧠", "💡", "🔮", "🧬", "⚗️", "🔭", "🛰️", "🚀", "🪐", "🌠", "☄️", "🌕", "🌖", "🌗", "🌘", "🏆", "🥇", "🥈", "🥉", "🎖️", "🏅", "🎗️", "💎", "👑", "⭐"],
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
            text=f"🔄 **Bot is Alive!**\n\n⏰ Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n🟢 Status: Active"
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
        return f"🌟 {result} 🌟"
    elif tier == "D":
        return f"👑✨ {result} ✨👑"
    return result

# ============ COMMAND HANDLERS ============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"🌟✨ **WELCOME {user.first_name}!** ✨🌟\n\n"
        f"💎 Premium Emoji Bot\n\n"
        f"📋 **Commands:**\n"
        f"/start - Welcome\n"
        f"/status - Check tier\n"
        f"/tiers - View tiers\n"
        f"/buy - Purchase premium\n"
        f"/redeem [code] - Redeem code\n"
        f"/help - Help\n\n"
        f"👑 **Owner:** `{OWNER_ID}`",
        parse_mode='Markdown'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "⚡ **COMMANDS** ⚡\n\n"
        "/start - Welcome message\n"
        "/status - Check your tier\n"
        "/tiers - View all tiers\n"
        "/buy - Purchase premium\n"
        "/redeem [code] - Redeem code\n"
        "/help - This message\n"
        "/expiry - Check expiry\n\n"
        "👑 Owner: `{}`".format(OWNER_ID),
        parse_mode='Markdown'
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    tier = user_tiers.get(user_id)
    if tier:
        tier_info = TIERS[tier]
        emoji_count = len(get_available_emojis(user_id))
        await update.message.reply_text(
            f"✨ **Your Status** ✨\n\n"
            f"{tier_info['color']} Tier: {tier_info['name']}\n"
            f"📊 Emojis: {emoji_count}\n"
            f"⏰ {get_tier_expiry_text(user_id)}",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            "⚠️ No premium tier.\n\n"
            "Use /buy to purchase or contact owner.",
            parse_mode='Markdown'
        )

async def tiers(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🌟 **TIERS** 🌟\n\n"
        "🟢 A - BASIC (FREE)\n"
        "🔵 B - SILVER (₹99/mo)\n"
        "🟡 C - GOLD (₹199/mo)\n"
        "🟣 D - PLATINUM (₹499/mo)\n\n"
        "Use /buy to purchase.",
        parse_mode='Markdown'
    )

async def gen_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        await update.message.reply_text("❌ Unauthorized!")
        return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /gen [A/B/C/D] [time]\nExample: /gen D 1mo")
        return
    tier = context.args[0].upper()
    time_str = context.args[1].lower()
    if tier not in TIERS:
        await update.message.reply_text("Invalid tier! Use A, B, C, D")
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
        await update.message.reply_text("Invalid time! Use: 1h, 2d, 1mo, 1y")
        return
    code, expiry = generate_code(tier, duration_hours)
    await update.message.reply_text(
        f"✅ Code: `{code}`\n"
        f"Tier: {TIERS[tier]['name']}\n"
        f"Expires: {expiry.strftime('%Y-%m-%d %H:%M:%S')}",
        parse_mode='Markdown'
    )

async def redeem_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if not context.args:
        await update.message.reply_text("Usage: /redeem [code]")
        return
    code = context.args[0].upper()
    if code not in active_codes:
        await update.message.reply_text("❌ Invalid code!")
        return
    code_data = active_codes[code]
    if datetime.now() > code_data["expiry"]:
        await update.message.reply_text("❌ Code expired!")
        return
    if code_data["used"]:
        await update.message.reply_text("❌ Code already used!")
        return
    tier = code_data["tier"]
    user_tiers[user_id] = tier
    user_tier_expiry[user_id] = code_data["expiry"]
    code_data["used"] = True
    await update.message.reply_text(
        f"✅ **Redeemed!**\n\n"
        f"Tier: {TIERS[tier]['name']}\n"
        f"Valid until: {code_data['expiry'].strftime('%Y-%m-%d %H:%M:%S')}",
        parse_mode='Markdown'
    )

async def buy_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🟢 Tier A - FREE", callback_data="buy_A")],
        [InlineKeyboardButton("🔵 Tier B - ₹99/mo", callback_data="buy_B")],
        [InlineKeyboardButton("🟡 Tier C - ₹199/mo", callback_data="buy_C")],
        [InlineKeyboardButton("🟣 Tier D - ₹499/mo", callback_data="buy_D")],
        [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]
    ]
    await update.message.reply_text(
        "💎 **Select Tier** 💎",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='Markdown'
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == "cancel":
        await query.edit_message_text("❌ Cancelled.")
        return
    if data.startswith("buy_"):
        tier = data.split("_")[1]
        if tier == "A":
            await query.edit_message_text("✅ Tier A is FREE! Just send messages!")
        else:
            keyboard = [[InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_{tier}")],
                       [InlineKeyboardButton("❌ Cancel", callback_data="cancel")]]
            await query.edit_message_text(
                f"📋 {TIERS[tier]['name']}\n💰 {TIERS[tier]['price']}\n\nConfirm?",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
    elif data.startswith("confirm_"):
        tier = data.split("_")[1]
        await context.bot.send_message(
            OWNER_ID,
            f"💰 Purchase: {TIERS[tier]['name']}\n👤 {query.from_user.first_name} (ID: {query.from_user.id})"
        )
        await query.edit_message_text("✅ Request sent! Contact owner for payment.")

async def expiry_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.effective_user.id)
    if user_id not in user_tiers:
        await update.message.reply_text("No active premium.")
        return
    await update.message.reply_text(
        f"⏰ {get_tier_expiry_text(user_id)}",
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
    
    print("🚀 Bot started!")
    app.run_polling()

if __name__ == "__main__":
    main()
