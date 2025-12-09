import os
import logging
import random

from functools import partial

from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)
from redis_client import (
    save_user_question,
    get_last_question,
    save_user_score,
    get_user_score
    )
from quiz_parser import (
    get_questions_answers,
    parsed_answer,
    normalize_answer
    )

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


NEW_QUESTION, USER_ANSWER = range(2)


def build_keyboard():
    custom_keyboard = [
        ['Новый вопрос', 'Счет'],
        ['Сдаться']
    ]
    return ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)


def start(update: Update, context: CallbackContext):
    context.bot.send_message(
        chat_id=update.effective_chat.id,
        text="""Привет! Я бот для викторины.\n
        Нажмите 'Новый воспрос' для того чтобы начать игру.""",
        reply_markup=build_keyboard()
        )
    return NEW_QUESTION


def handle_new_question_request(update: Update, context: CallbackContext, quiz_map):
    user_id = update.message.from_user.id

    random_question = random.choice(list(quiz_map.keys()))
    save_user_question(user_id, random_question, platform='tg')

    update.message.reply_text(
        random_question
    )
    return USER_ANSWER


def handle_solution_attempt(update: Update, context: CallbackContext, quiz_map, keyboard):
    user_id = update.message.from_user.id

    last_question = get_last_question(user_id, platform='tg')

    if not last_question:
        text = 'Сначала нажмите "Новый вопрос"'
        update.message.reply_text(update, text, keyboard)
        return NEW_QUESTION

    parsed = parsed_answer(quiz_map[last_question])

    normalized_user = normalize_answer(update.message.text)
    normalized_correct = normalize_answer(parsed['correct_answer'])
    normalized_accepted = normalize_answer(parsed['accepted_answer'])

    is_correct = (
        normalized_user == normalized_correct
        or (parsed['accepted_answer'] and normalized_user == normalized_accepted)
    )
    if is_correct:
        save_user_score(user_id, platform='tg')
        text = f"Верно!\n\n{parsed['explanation']}"
        update.message.reply_text(update, text, keyboard)
        return NEW_QUESTION
    else:
        text = "Неверно! Попробуйте ещё"
        update.message.reply_text(update, text)
        return USER_ANSWER


def handle_score(update: Update, context: CallbackContext, keyboard):
    user_id = update.message.from_user.id
    score = get_user_score(user_id, platform='tg')

    text = f"Ваш счет: {score}"
    update.message.reply_text(update, text, keyboard)
    return NEW_QUESTION


def handle_surrender_and_new_question(update: Update, context: CallbackContext, quiz_map, keyboard):
    user_id = update.message.from_user.id
    last_question = get_last_question(user_id, platform='tg')

    if not last_question:
        text = 'У вас нет активного вопроса,\nнажмите "Новый вопрос"'
        update.message.reply_text(update, text, keyboard)
        return NEW_QUESTION

    parsed = parsed_answer(quiz_map[last_question])

    text = f"""Правильный ответ:\n{parsed['correct_answer']}
        \n\n{parsed['explanation']}"""
    update.message.reply_text(update, text, keyboard)
    return handle_new_question_request(update, context, quiz_map)


def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    load_dotenv()
    api_key = os.environ['TG_BOT_API_KEY']

    updater = Updater(api_key, use_context=True)
    dispatcher = updater.dispatcher

    quiz_map = get_questions_answers()
    keyboard = build_keyboard()

    conversation_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            NEW_QUESTION: [
                MessageHandler(
                    Filters.regex(r"^Новый вопрос$"),
                    partial(
                        handle_new_question_request,
                        quiz_map=quiz_map
                        )
                ),
                MessageHandler(
                    Filters.regex(r"^Сдаться$"),
                    partial(
                        handle_surrender_and_new_question,
                        quiz_map=quiz_map,
                        keyboard=keyboard
                        )
                ),
                MessageHandler(
                    Filters.regex(r"^Счет$"),
                    partial(
                        handle_score,
                        keyboard=keyboard
                        )
                )],
            USER_ANSWER: [
                MessageHandler(
                    Filters.regex(r"^Сдаться$"),
                    partial(
                        handle_surrender_and_new_question,
                        quiz_map=quiz_map,
                        keyboard=keyboard
                        )
                ),
                MessageHandler(
                    Filters.regex(r"^Счет$"),
                    partial(
                        handle_score,
                        keyboard=keyboard
                        )
                ),
                MessageHandler(
                    Filters.text & ~Filters.command,
                    partial(
                        handle_solution_attempt,
                        quiz_map=quiz_map,
                        keyboard=keyboard
                        )
                )]
        },
        fallbacks=[]
    )

    dispatcher.add_handler(conversation_handler)

    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
