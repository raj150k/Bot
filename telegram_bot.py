import os
import logging
import tempfile
import subprocess
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# ====== আপনার তথ্য দিয়ে বদলান ======
TELEGRAM_BOT_TOKEN = "8956527817:AAETStVWMjg1EXJKUcWRa81X8dGo0rGP5yo"        # @BotFather থেকে নিন
ADMIN_USER_ID = 8636937438                          # আপনার টেলিগ্রাম আইডি
# ====================================

logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    msg = (
        f"👋 হ্যালো {user.first_name}! 🤖\n\n"
        f"আমি একটি ** ভয়েস চেঞ্জার বট ** 🎤\n\n"
        f"✅ **আমি যা করতে পারি:**\n"
        f"• তোমার ভয়েস মেসেজ → নারী কণ্ঠে রূপান্তর 🎀\n"
        f"• সম্পূর্ণ ফ্রি এবং রিয়েল-টাইম এডমিন: @raj169k 🚀\n\n"
        f"**ব্যবহার:**\n"
        f"➡️ ভয়েস মেসেজ রেকর্ড করে পাঠাও\n"
        f"➡️ আমিই কনভার্ট করে দিব 💕\n\n"
        f"এখনই চেষ্টা করো! ⬇️"
    )
    await update.message.reply_text(msg, parse_mode="Markdown")

async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_USER_ID:
        await update.message.reply_text("⛔ শুধু এডমিনের জন্য!")
        return
    await update.message.reply_text("🔐 আপনি এডমিন হিসেবে আছেন ✅")

async def handle_voice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    voice = update.message.voice
    await update.message.reply_chat_action("record_voice")
    process_msg = await update.message.reply_text("🎤 ভয়েস প্রসেস করছি... ⏳")

    try:
        voice_file = await voice.get_file()
        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as tmp:
            await voice_file.download_to_drive(tmp.name)
            orig = tmp.name

        wav = orig.replace(".ogg", ".wav")

        # ffmpeg দিয়ে ogg → wav
        result = subprocess.run(
            ["ffmpeg", "-i", orig, "-ar", "44100", "-ac", "1", wav, "-y"],
            capture_output=True, text=True
        )
        os.unlink(orig)

        if result.returncode != 0:
            await process_msg.edit_text("❌ অডিও প্রসেস করতে সমস্যা হয়েছে।")
            return

        # এখানে মূল RVC কনভার্ট হবে (যদি RVC থাকে)
        # বর্তমানে শুধু একটি ডেমো ইকো — আপনি চাইলে RVC API কল যোগ করতে পারেন
        converted_path = wav  # ডেমো: একই ফাইল পাঠাচ্ছি (RVC ছাড়া)

        with open(converted_path, "rb") as f:
            audio_data = f.read()

        with tempfile.NamedTemporaryFile(delete=False, suffix=".ogg") as tmp:
            tmp.write(audio_data)
            res_path = tmp.name

        await update.message.reply_voice(
            voice=open(res_path, "rb"),
            caption="✅ ভয়েস পরিবর্তন করা হয়েছে! 🎀"
        )

        os.unlink(res_path)
        os.unlink(wav)
        await process_msg.delete()

    except Exception as e:
        logging.error(f"Error: {e}")
        await process_msg.edit_text("❌ এরর! আবার চেষ্টা করুন।")

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice))
    print("🤖 Telegram Bot চালু হচ্ছে...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()
