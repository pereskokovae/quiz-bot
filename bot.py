import os
import logging
import random

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Updater, MessageHandler, Filters, CallbackContext, CommandHandler
    )
from functools import partial

from redis_client import save_user_question, get_last_question, save_user_score, get_user_score
from serializer_json import get_questions_answers, parse_answer, normalize_answer


from dotenv import load_dotenv


logger = logging.getLogger(__name__)


def start(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="Привет! Я бот для викторины"
        )


def handle_new_question(update, user_id, quiz_map, reply_markup):
    random_question = random.choice(list(quiz_map.keys()))
    save_user_question(user_id, random_question)

    update.message.reply_text(
        random_question,
        reply_markup=reply_markup
    )


def handle_score(update, user_id, reply_markup):
    score = get_user_score(user_id)

    update.message.reply_text(
        f"Ваш счет: {score}",
        reply_markup=reply_markup
    )


def handle_surrender(update, user_id, quiz_map, reply_markup):
    last_question = get_last_question(user_id)

    if not last_question:
        update.message.reply_text(
            'У вас нет активного вопроса,\nнажмите "Новый вопрос"',
            reply_markup=reply_markup
        )
        return

    parsed = parse_answer(quiz_map[last_question])
    correct_answer = (
        f"Правильный ответ:\n{parsed['correct_answer']}\n\n"
        f"{parsed['explanation']}"
    )

    update.message.reply_text(
        correct_answer,
        reply_markup=reply_markup
    )


def handle_answer(update, user_message, user_id, quiz_map, reply_markup):
    last_question = get_last_question(user_id)

    if not last_question:
        update.message.reply_text(
            'Сначала нажмите "Новый вопрос"',
            reply_markup=reply_markup
        )
        return

    parsed = parse_answer(quiz_map[last_question])

    normalized_user = normalize_answer(user_message)
    normalized_correct = normalize_answer(parsed['correct_answer'])
    normalized_accepted = normalize_answer(parsed['accepted_answer'])

    is_correct = (
        normalized_user == normalized_correct
        or (parsed['accepted_answer'] and normalized_user == normalized_accepted)
    )
    if is_correct:
        save_user_score(user_id)
        update.message.reply_text(
            f"Верно!\n\n{parsed['explanation']}",
            reply_markup=reply_markup
        )
    else:
        update.message.reply_text(
            "Неверно! Попробуйте ещё",
            reply_markup=reply_markup
        )


def handle_tg_message(update: Update, context: CallbackContext, quiz_map):
    user_message = update.message.text
    user_id = update.message.from_user.id

    custom_keyboard = [
        ['Новый вопрос', 'Счет'],
        ['Сдаться']
    ]

    reply_markup = ReplyKeyboardMarkup(custom_keyboard)
    if user_message == 'Новый вопрос':
        return handle_new_question(update, user_id, quiz_map, reply_markup)

    if user_message == 'Счет':
        return handle_score(update, user_id, reply_markup)

    if user_message == 'Сдаться':
        return handle_surrender(update, user_id, quiz_map, reply_markup)

    return handle_answer(update, user_message, user_id, quiz_map, reply_markup)


def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )
    load_dotenv()

    api_key = os.environ['API_KEY_TG_BOT']
    updater = Updater(api_key, use_context=True)

    quiz_map = get_questions_answers()

    dispatcher = updater.dispatcher
    echo_handler = partial(
        handle_tg_message,
        quiz_map=quiz_map
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
