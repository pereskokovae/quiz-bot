import os
import random
import logging

import vk_api as vk
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

from redis_client import (
    save_user_question,
    get_last_question,
    save_user_score,
    get_user_score
    )
from serializer import (
    get_questions_answers,
    parsed_answer,
    normalize_answer
    )

from dotenv import load_dotenv

logger = logging.getLogger(__name__)


def build_keyboard():
    keyboard = VkKeyboard(one_time=False)

    keyboard.add_button('Новый вопрос', color=VkKeyboardColor.PRIMARY)
    keyboard.add_button('Счет', color=VkKeyboardColor.SECONDARY)

    keyboard.add_line()
    keyboard.add_button('Сдаться', color=VkKeyboardColor.SECONDARY)

    return keyboard.get_keyboard()


def send_message(vk_api, user_id, text, keyboard):
    random_id = random.randint(1, 1000)
    vk_api.messages.send(
        user_id=user_id,
        message=text,
        keyboard=keyboard,
        random_id=random_id
    )


def handle_new_question_request(vk_api, user_id, quiz_map):
    random_question = random.choice(list(quiz_map.keys()))
    save_user_question(user_id, random_question)

    send_message(vk_api, user_id, random_question, keyboard=None)


def handle_score(vk_api, user_id, keyboard):
    score = get_user_score(user_id)
    text = f"Ваш счет: {score}"
    send_message(vk_api, user_id, text, keyboard)


def handle_surrender_and_new_question(vk_api, user_id, quiz_map, keyboard):
    last_question = get_last_question(user_id)

    if not last_question:
        text = 'У вас нет активного вопроса,\nнажмите "Новый вопрос"'
        send_message(vk_api, user_id, text, keyboard)
        return

    parsed = parsed_answer(quiz_map[last_question])
    text = f"""Правильный ответ:\n{parsed['correct_answer']}
        \n\n{parsed['explanation']}"""
    send_message(vk_api, user_id, text, keyboard)
    handle_new_question_request(vk_api, user_id, quiz_map)


def handle_solution_attempt(vk_api, user_id, text, quiz_map, keyboard):
    last_question = get_last_question(user_id)

    if not last_question:
        text = 'Сначала нажмите "Новый вопрос"'
        send_message(vk_api, user_id, text, keyboard)
        return

    parsed = parsed_answer(quiz_map[last_question])

    normalized_user = normalize_answer(text)
    normalized_correct = normalize_answer(parsed['correct_answer'])
    normalized_accepted = normalize_answer(parsed['accepted_answer'])

    is_correct = (
        normalized_user == normalized_correct
        or (parsed['accepted_answer'] and normalized_user == normalized_accepted)
    )
    if is_correct:
        save_user_score(user_id)
        text = f"Верно!\n\n{parsed['explanation']}",
        send_message(vk_api, user_id, text, keyboard)
    else:
        text = "Неверно! Попробуйте ещё"
        send_message(vk_api, user_id, text, keyboard=None)


def handle_vk_message(vk_api, event, keyboard):
    user_id = event.user_id
    text = event.text.strip()
    quiz_map = get_questions_answers()

    if event.text == "Новый вопрос":
        return handle_new_question_request(vk_api, user_id, quiz_map)

    if event.text == "Счет":
        return handle_score(vk_api, user_id, keyboard)

    if event.text == "Сдаться":
        return handle_surrender_and_new_question(vk_api, user_id, quiz_map, keyboard)

    return handle_solution_attempt(vk_api, user_id, text, quiz_map, keyboard)


def main():
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=logging.INFO
    )

    load_dotenv()
    api_key = os.environ['VK_BOT_API_KEY']

    vk_session = vk.VkApi(token=api_key)
    vk_api = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)

    keyboard = build_keyboard()

    logging.info("Бот запущен!")

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            try:
                handle_vk_message(vk_api, event, keyboard)
            except Exception as e:
                logging.error(e)


if __name__ == '__main__':
    main()
