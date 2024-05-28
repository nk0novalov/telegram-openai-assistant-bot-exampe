import time

from openai import OpenAI
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackContext
import os


assistant_id = os.getenv("ASSISTANT_ID", "YOUR_ASSISTANT_ID_FROM_OPEN_AI_FOR_DEBUG")
client_api_key_openai = os.getenv("CLIENT_API_KEY", "YOUR_CLIENT_API_KEY_FOR_DEBUG")
telegram_bot_token = os.getenv("TELEGRAM_TOKEN", "YOUR_TELEGRAM_BOT_TOKEN_FOR_DEBUG")

client = OpenAI(api_key=client_api_key_openai)


async def start(update: Update, context: CallbackContext) -> None:
    thread = client.beta.threads.create()
    context.user_data['openai_thread'] = thread.id
    await update.message.reply_text("Hello!")


async def process_message_with_open_ai(update: Update, context: CallbackContext):
    client.beta.threads.messages.create(
        thread_id=context.user_data['openai_thread'],
        role="user", content=update.message.text
    )

    run = client.beta.threads.runs.create(
        thread_id=context.user_data['openai_thread'],
        assistant_id=assistant_id,
    )

    while True:
        run = client.beta.threads.runs.retrieve(thread_id=context.user_data['openai_thread'],
                                                run_id=run.id)
        if run.status == "completed":
            break
        time.sleep(0.1)

    messages = client.beta.threads.messages.list(thread_id=context.user_data['openai_thread'])
    response = messages.dict()["data"][0]["content"][0]["text"]["value"]
    await update.message.reply_text(response)


def main():
    application = Application.builder().token(telegram_bot_token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT, process_message_with_open_ai))
    application.run_polling()


if __name__ == "__main__":
    main()
