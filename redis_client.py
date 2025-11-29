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
    question_number = redis.llen(key) + 1

    redis.rpush(key, question)
    return question_number


if __name__ == "__main__":
    get_redis()
