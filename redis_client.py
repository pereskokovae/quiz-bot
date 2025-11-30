import redis
import os
import logging
from dotenv import load_dotenv


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
    )
logger = logging.getLogger(__name__)


def get_redis():
    load_dotenv()

    try:
        client = redis.Redis(
            host=os.getenv('REDIS_HOST'),
            port=os.getenv('REDIS_PORT'),
            decode_responses=True,
            username=os.getenv('REDIS_USERNAME', 'default'),
            password=os.getenv('REDIS_PASSWORD'),
        )
        return client
    except Exception as e:
        logger.warning(e)


def save_user_question(user_id, question):
    redis = get_redis()
    key = f"user:{user_id}:questions"
    redis.set(key, question)


def get_last_question(user_id):
    redis = get_redis()
    key = f"user:{user_id}:questions"
    last_question = redis.get(key)
    return last_question


def save_user_score(user_id):
    redis = get_redis()
    key = f"user{user_id}:score"
    current_score = redis.get(key)
    if not current_score:
        score = 1
    else:
        score = int(current_score) + 1
        redis.set(key, score)


def get_user_score(user_id):
    redis = get_redis()
    key = f"user{user_id}:score"
    score = redis.get(key)
    if score is None:
        score = 0
        return score
    return score
