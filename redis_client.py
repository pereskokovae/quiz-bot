import redis
import os
import logging
from dotenv import load_dotenv

load_dotenv()


logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
    )


REDIS = redis.Redis.from_url(
    os.getenv('REDIS_URL'), decode_responses=True
    )


def save_user_question(user_id, question):
    key = f"user:{user_id}:questions"
    REDIS.set(key, question)


def get_last_question(user_id):
    key = f"user:{user_id}:questions"
    last_question = REDIS.get(key)
    return last_question


def save_user_score(user_id):
    key = f"user{user_id}:score"
    current_score = REDIS.get(key)
    if not current_score:
        score = 1
    else:
        score = int(current_score) + 1
        REDIS.set(key, score)


def get_user_score(user_id):
    key = f"user:{user_id}:score"
    score = REDIS.get(key)
    if score is None:
        score = 0
        return score
    return score
