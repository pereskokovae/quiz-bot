import os
import logging
import random
import json

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Updater, MessageHandler, Filters, CallbackContext, CommandHandler
    )
from functools import partial

from redis_client import save_user_question

from dotenv import load_dotenv


logger = logging.getLogger(__name__)


def get_questions_answers():
    questions = []
    answers = []
    with open('quiz_questions.json', 'r', encoding='utf-8') as file:
        quiz_questions = json.load(file)
        for quiz_question in quiz_questions:
            questions.append(quiz_question['question'])
            answers.append(quiz_question['answer'])
    return questions, answers


def start(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Привет! Я бот для викторины"
        )


def handle_tg_message(update: Update, context: CallbackContext, questions, answers) -> None:
    user_message = update.message.text
    user_id = update.message.from_user.id

    custom_keyboard = [
        ['Новый вопрос', 'Счет'],
        ['Сдаться']
    ]

    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    if user_message == 'Новый вопрос':
        random_question = random.choice(questions)
        save_user_question(user_id, random_question)
        update.message.reply_text(
                random_question,
                reply_markup=reply_markup
            )


def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    load_dotenv()

    api_key = os.environ['API_KEY_TG_BOT']
    updater = Updater(api_key, use_context=True)

    questions, answers = get_questions_answers()

    dispatcher = updater.dispatcher
    echo_handler = partial(
        handle_tg_message,
        questions=questions,
        answers=answers
    )
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(MessageHandler(
        Filters.text & ~Filters.command,
        echo_handler
    ))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()