import os
import logging

from telegram import Update
from telegram.ext import (
    Updater, MessageHandler, Filters, CallbackContext, CommandHandler
    )

from dotenv import load_dotenv


logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Здравствуйте!"
        )


def echo(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(update.message.text)


def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    load_dotenv()

    api_key = os.environ['API_KEY_TG_BOT']
    updater = Updater(api_key)

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()