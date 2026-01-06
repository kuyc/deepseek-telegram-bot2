import os
from openai import OpenAI
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    filters
)

# ================== ENV ==================

BOT_TOKEN = os.getenv("BOT_TOKEN")
MS_API_KEY = os.getenv("MS_API_KEY")

# DEBUG — СМОТРИ В LOGS
print("BOT_TOKEN =", BOT_TOKEN)
print("MS_API_KEY =", MS_API_KEY)

# ================== DEEPSEEK ==================

client = None
if MS_API_KEY:
    client = OpenAI(
        base_url="https://api-inference.modelscope.ai/v1",
        api_key=MS_API_KEY,
    )

def ask_deepseek(text: str) -> str:
    if not client:
        return "❌ MS_API_KEY не найден. Проверь Variables в Railway."

    try:
        response = client.chat.completions.create(
            model="deepseek-ai/DeepSeek-V3.2",
            messages=[{"role": "user", "content": text}],
            extra_body={"enable_thinking": False}
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Ошибка DeepSeek: {e}"

# ================== ЛИЧКА ==================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "✅ Бот работает.\n"
        "Добавь меня в канал как администратора — я буду отвечать на сообщения."
    )

# ================== КАНАЛ ==================

async def channel_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.channel_post
    if not message or not message.text:
        return

    answer = ask_deepseek(message.text)

    await context.bot.send_message(
        chat_id=message.chat_id,
        text=answer,
        reply_to_message_id=message.message_id
    )

# ================== MAIN ==================

def main():
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN не найден. Проверь Variables в Railway.")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(
        MessageHandler(filters.ChatType.CHANNEL, channel_message)
    )

    print("Бот запущен")
    app.run_polling()

if __name__ == "__main__":
    main()
