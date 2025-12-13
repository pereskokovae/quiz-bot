import redis
import os
import logging
from dotenv import load_dotenv


logger = logging.getLogger(__name__)


def connect_to_redis(redis_url):
    return redis.Redis.from_url(
        redis_url, decode_responses=True
    )


def save_user_question(user_id, platform, question):
    key = f"{platform}user:{user_id}:questions"
    connect_to_redis.set(key, question)


def get_last_question(user_id, platform):
    key = f"{platform}user:{user_id}:questions"
    last_question = connect_to_redis.get(key)
    return last_question


def save_user_score(user_id, platform):
    key = f"{platform}user{user_id}:score"
    current_score = connect_to_redis.get(key)
    if not current_score:
        score = 1
    else:
        score = int(current_score) + 1
        connect_to_redis.set(key, score)


def get_user_score(user_id, platform):
    key = f"{platform}user:{user_id}:score"
    score = connect_to_redis.get(key)
    if score is None:
        score = 0
        return score
    return score


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    load_dotenv()

    redis_url = os.getenv('REDIS_URL')
    connect_to_redis(redis_url)
